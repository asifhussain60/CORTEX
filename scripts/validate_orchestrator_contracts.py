#!/usr/bin/env python3
"""
Orchestrator Contract Validation Script.

Validates all wired orchestrators against IOrchestrator contract and logs results
to contract_validation_audit.db. Run this as part of CI/CD pipeline or manually
to populate the audit database.

Usage:
    python3 scripts/validate_orchestrator_contracts.py
"""
from pathlib import Path
import sys

# Add cortex to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from cortex.core.wiring.registry.contract_validator import ContractValidator


def main() -> int:
    """Run contract validation for all orchestrators."""
    print("=" * 80)
    print("CORTEX Orchestrator Contract Validation")
    print("=" * 80)
    
    # Initialize validator (automatically creates .cortex-runtime/wiring/contract_validation_audit.db)
    validator = ContractValidator()
    print(f"✓ Initialized ContractValidator")
    print(f"  Audit DB: {validator.audit_db}")
    
    # List of all wired orchestrators (from wiring specs)
    orchestrators = [
        "MasterOrchestrator",
        "IntentRouter",
        "TDDOrchestrator",
        "EnforcementOrchestrator",
        "TestClassifierOrchestrator",
        "StateOrchestrator",
        "InteractionOrchestrator",
        "DomainOrchestrator",
        "IntelligenceOrchestrator",
        "OnboardingOrchestrator",
        "ConversationOrchestrator",
        "ObservabilityOrchestrator",
        "ArchitectureOrchestrator",
        "SweepCatalogueOrchestrator",
        "DigestSessionOrchestrator",
        "BulkDigestOrchestrator",
        "DashboardOrchestrator",
        "KnowledgeSynthesisOrchestrator",
        "DocumentOrchestrator",
        "RefactorOrchestrator",
        "DeploymentOrchestrator",
        "EmbeddingsOrchestrator",
    ]
    
    print(f"\n📋 Validating {len(orchestrators)} orchestrators...")
    print("-" * 80)
    
    # Validate all orchestrators
    results = validator.validate_all_orchestrators(orchestrators)
    
    # Track contract versions
    for orch in orchestrators:
        validator.track_contract_evolution(orch, version="1.0")
    
    print(f"\n✅ Validation complete!")
    print(f"   Total: {len(results)} orchestrators")
    print(f"   Passed: {sum(1 for r in results if r.is_valid)}")
    print(f"   Failed: {sum(1 for r in results if not r.is_valid)}")
    
    # Display summary
    summary = validator.get_validation_summary()
    print(f"\n📊 Audit Database Summary:")
    print(f"   Total validations: {summary['total_validations']}")
    print(f"   Passed: {summary['passed']}")
    print(f"   Failed: {summary['failed']}")
    
    print(f"\n💾 Audit database populated at:")
    print(f"   {validator.audit_db}")
    print("=" * 80)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
