"""
Wiring Contract Manager - AC-PERMANENT-FIX-016

Manages the deterministic wiring contract that serves as the single source of truth
for all orchestrator definitions. This contract:

1. Is computed once on first CORTEX import
2. Is cached in-process for O(1) lookups
3. Is embedded in the CORTEX codebase (cortex/__wiring_contract__.yaml)
4. Is compared against runtime state by MCP health-check
5. Enables permanent wiring fixes (no repeated discovery)

This ensures all repos and machines stay synchronized.
"""

import hashlib
import json
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, Any, List

import yaml

logger = logging.getLogger(__name__)


@dataclass
class WiringContractEntry:
    """Single orchestrator entry in the wiring contract."""
    name: str
    module: str
    class_name: str
    priority: int
    capabilities: List[str]
    dependencies: Optional[List[str]] = None
    is_optional: bool = False
    version: str = "1.0.0"

    def __post_init__(self) -> None:
        if self.dependencies is None:
            self.dependencies = []


@dataclass
class WiringContract:
    """
    Wiring contract - immutable specification of all orchestrators.
    
    This is the ground truth for:
    - What orchestrators should exist
    - Their wiring order
    - Their capabilities
    - Their dependencies
    """
    version: str
    cortex_version: str
    computed_at: str
    checksum: str
    total_orchestrators: int
    wired_orchestrators: int
    orchestrators: List[WiringContractEntry]
    status: str = "VALID"

    def to_yaml_dict(self) -> Dict[str, Any]:
        """Convert to YAML-serializable dict."""
        return {
            "version": self.version,
            "cortex_version": self.cortex_version,
            "computed_at": self.computed_at,
            "checksum": self.checksum,
            "total_orchestrators": self.total_orchestrators,
            "wired_orchestrators": self.wired_orchestrators,
            "status": self.status,
            "orchestrators": [
                {
                    "name": o.name,
                    "module": o.module,
                    "class_name": o.class_name,
                    "priority": o.priority,
                    "capabilities": o.capabilities,
                    "dependencies": o.dependencies or [],
                    "is_optional": o.is_optional,
                    "version": o.version,
                }
                for o in self.orchestrators
            ]
        }


class WiringContractManager:
    """
    Manages the wiring contract singleton.
    
    Lifecycle:
    1. First import: Load contract from CORTEX codebase
    2. Cache in-process (immutable)
    3. Compare against runtime state via MCP health-check
    4. Flag drift for pre-op gates
    """

    _instance: Optional['WiringContractManager'] = None
    _contract: Optional[WiringContract] = None
    _cached_at: Optional[datetime] = None

    @classmethod
    def instance(cls) -> 'WiringContractManager':
        """Get singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def reset_instance(cls):
        """Reset singleton (for testing)."""
        cls._instance = None
        cls._contract = None
        cls._cached_at = None

    def get_contract(self) -> WiringContract:
        """
        Get cached contract, loading if necessary.
        
        Returns:
            WiringContract (immutable)
        """
        if self._contract is not None and self._cached_at is not None:
            age_ms = (datetime.now(timezone.utc) - self._cached_at).total_seconds() * 1000
            logger.debug(f"Using cached contract (age: {age_ms:.0f}ms)")
            return self._contract

        # Load from embedded file
        contract = self._load_contract_from_codebase()
        if contract is None:
            logger.error("Failed to load wiring contract from CORTEX codebase")
            raise RuntimeError("CORTEX wiring contract not found - system not properly initialized")

        self._contract = contract
        self._cached_at = datetime.now(timezone.utc)

        logger.info(
            f"✅ Loaded wiring contract: {contract.total_orchestrators} orchestrators, "
            f"checksum: {contract.checksum[:8]}..."
        )
        return self._contract

    def compute_contract_checksum(self, orchestrators: List[WiringContractEntry]) -> str:
        """
        Compute deterministic SHA256 checksum of orchestrator definitions.
        
        Args:
            orchestrators: List of orchestrator entries
            
        Returns:
            SHA256 checksum (first 32 chars)
        """
        # Sort for determinism
        sorted_names = sorted([o.name for o in orchestrators])
        sorted_capabilities = sorted(
            [f"{o.name}:{','.join(sorted(o.capabilities))}" for o in orchestrators]
        )

        # Create deterministic string
        state_str = json.dumps({
            "names": sorted_names,
            "capabilities": sorted_capabilities,
        }, sort_keys=True)

        # Compute hash
        hash_obj = hashlib.sha256(state_str.encode())
        return hash_obj.hexdigest()[:32]

    def create_contract(
        self,
        orchestrators: List[WiringContractEntry],
        cortex_version: str = "5.1",
    ) -> WiringContract:
        """
        Create a new wiring contract from orchestrator definitions.
        
        Args:
            orchestrators: List of orchestrator configurations
            cortex_version: CORTEX version string
            
        Returns:
            WiringContract
        """
        checksum = self.compute_contract_checksum(orchestrators)

        contract = WiringContract(
            version="1.0",
            cortex_version=cortex_version,
            computed_at=datetime.now(timezone.utc).isoformat(),
            checksum=checksum,
            total_orchestrators=len(orchestrators),
            wired_orchestrators=len([o for o in orchestrators if not o.is_optional]),
            orchestrators=orchestrators,
            status="VALID",
        )

        logger.info(f"Created wiring contract with checksum: {checksum[:8]}...")
        return contract

    def _load_contract_from_codebase(self) -> Optional[WiringContract]:
        """
        Load contract from embedded CORTEX file: cortex/__wiring_contract__.yaml
        
        This is the single source of truth for all orchestrators.
        
        Returns:
            WiringContract if found, None otherwise
        """
        try:
            # Locate contract file in CORTEX package
            cortex_root = Path(__file__).parent.parent
            contract_file = cortex_root / "__wiring_contract__.yaml"

            if not contract_file.exists():
                logger.warning(f"Contract file not found: {contract_file}")
                logger.info("Generating contract from canonical orchestrator definitions...")

                # Fallback: generate from db_wiring_init.py
                return self._generate_contract_from_definitions()

            # Load from file
            with open(contract_file, "r") as f:
                data = yaml.safe_load(f)

            # Parse into WiringContract
            orchestrators = [
                WiringContractEntry(
                    name=o["name"],
                    module=o["module"],
                    class_name=o["class_name"],
                    priority=o.get("priority", 100),
                    capabilities=o.get("capabilities", []),
                    dependencies=o.get("dependencies", []),
                    is_optional=o.get("is_optional", False),
                    version=o.get("version", "1.0.0"),
                )
                for o in data.get("orchestrators", [])
            ]

            contract = WiringContract(
                version=data.get("version", "1.0"),
                cortex_version=data.get("cortex_version", "5.1"),
                computed_at=data.get("computed_at", datetime.now(timezone.utc).isoformat()),
                checksum=data.get("checksum", ""),
                total_orchestrators=data.get("total_orchestrators", len(orchestrators)),
                wired_orchestrators=data.get("wired_orchestrators", len(orchestrators)),
                orchestrators=orchestrators,
                status=data.get("status", "VALID"),
            )

            logger.debug(f"✅ Loaded contract from {contract_file}")
            return contract

        except Exception as e:
            logger.error(f"Failed to load contract: {e}")
            return None

    def _generate_contract_from_definitions(self) -> Optional[WiringContract]:
        """
        Generate contract from canonical db_wiring_init.py definitions.
        
        Fallback if __wiring_contract__.yaml doesn't exist yet.
        
        Returns:
            WiringContract or None
        """
        try:
            from cortex.orchestrators.core.db_wiring_init import ALL_ORCHESTRATORS

            entries = [
                WiringContractEntry(
                    name=config.name,
                    module=config.module_path,
                    class_name=config.class_name,
                    priority=config.priority,
                    capabilities=config.capabilities,
                    dependencies=config.dependencies,
                    is_optional=config.is_optional,
                    version=config.version,
                )
                for config in ALL_ORCHESTRATORS
            ]

            contract = self.create_contract(entries)
            logger.info(f"Generated contract from db_wiring_init.py ({len(entries)} orchestrators)")
            return contract

        except Exception as e:
            logger.error(f"Failed to generate contract: {e}")
            return None

    def save_contract_to_file(self, contract: WiringContract) -> bool:
        """
        Save contract to cortex/__wiring_contract__.yaml for version control.
        
        Args:
            contract: WiringContract to save
            
        Returns:
            True if successful, False otherwise
        """
        try:
            cortex_root = Path(__file__).parent.parent
            contract_file = cortex_root / "__wiring_contract__.yaml"

            with open(contract_file, "w") as f:
                yaml.dump(contract.to_yaml_dict(), f, default_flow_style=False)

            logger.info(f"✅ Saved contract to {contract_file}")
            return True

        except Exception as e:
            logger.error(f"Failed to save contract: {e}")
            return False

    def compare_with_runtime_state(self, runtime_orchestrators: List[str]) -> Dict[str, Any]:
        """
        Compare contract against current runtime state.
        
        Used by MCP health-check to detect drift.
        
        Args:
            runtime_orchestrators: List of currently wired orchestrator names
            
        Returns:
            Comparison results with added/removed/changed orchestrators
        """
        contract = self.get_contract()
        contract_names = set(o.name for o in contract.orchestrators)
        runtime_names = set(runtime_orchestrators)

        return {
            "drift_detected": contract_names != runtime_names,
            "expected_count": len(contract_names),
            "actual_count": len(runtime_names),
            "added": list(runtime_names - contract_names),
            "removed": list(contract_names - runtime_names),
            "valid": list(contract_names & runtime_names),
            "contract_checksum": contract.checksum,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def validate_contract_integrity(self) -> Dict[str, Any]:
        """
        Validate that contract is intact and valid.
        
        Returns:
            Validation results
        """
        try:
            contract = self.get_contract()

            # Verify checksum
            computed_checksum = self.compute_contract_checksum(contract.orchestrators)
            checksum_valid = computed_checksum == contract.checksum

            # Verify orchestrator count
            count_valid = contract.total_orchestrators == len(contract.orchestrators)

            # Verify no duplicates
            names = [o.name for o in contract.orchestrators]
            no_duplicates = len(names) == len(set(names))

            return {
                "valid": checksum_valid and count_valid and no_duplicates,
                "checksum_valid": checksum_valid,
                "count_valid": count_valid,
                "no_duplicates": no_duplicates,
                "total_orchestrators": len(contract.orchestrators),
                "status": contract.status,
                "issues": [
                    "Checksum mismatch" if not checksum_valid else None,
                    "Count mismatch" if not count_valid else None,
                    "Duplicate orchestrators found" if not no_duplicates else None,
                ],
            }

        except Exception as e:
            logger.error(f"Contract integrity check failed: {e}")
            return {
                "valid": False,
                "error": str(e),
            }
