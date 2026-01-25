"""
CORTEX Test Isolation Mechanisms
Ensures clean state for DatabaseBackedRegistry and prevents test contamination.

AC-PERMANENT-FIX-010: Test isolation mechanisms for production registry integrity
"""

import logging
import os
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger(__name__)


class TestIsolationEnforcer:
    """
    Enforces clean test isolation for production components.
    
    Prevents the "orphan" orchestrator issue identified in chat01.md where
    test data contaminated the production DatabaseBackedRegistry.
    """
    
    @staticmethod
    def reset_database_registry() -> Dict[str, Any]:
        """
        Reset DatabaseBackedRegistry singleton and clean test artifacts.
        
        Returns:
            Dict with isolation status and actions taken
        """
        result = {
            "singleton_reset": False,
            "database_cleaned": False,
            "contamination_detected": False,
            "clean_state": False,
            "actions": []
        }
        
        try:
            # Step 1: Reset singleton instance
            from cortex.orchestrators.core.database_registry import DatabaseBackedRegistry
            DatabaseBackedRegistry.reset_instance()
            result["singleton_reset"] = True
            result["actions"].append("Reset DatabaseBackedRegistry singleton")
            
            # Step 2: Remove test database files
            test_db_paths = [
                ".cortex/orchestrator_registry.db",
                "tests/.cortex/orchestrator_registry.db", 
                ".cortex/test_orchestrator_registry.db"
            ]
            
            for db_path in test_db_paths:
                if os.path.exists(db_path):
                    os.remove(db_path)
                    result["database_cleaned"] = True
                    result["actions"].append(f"Removed test database: {db_path}")
            
            # Step 3: Check for test contamination
            fresh_registry = DatabaseBackedRegistry.instance()
            
            # Check for problematic test orchestrators
            contaminated_names = ["orphan", "test_orchestrator", "dummy", "fake"]
            orchestrator_names = list(fresh_registry._orchestrators.keys())
            
            contamination = any(name in orchestrator_names for name in contaminated_names)
            if contamination:
                result["contamination_detected"] = True
                result["actions"].append("CONTAMINATION: Test orchestrators found in fresh instance")
            else:
                result["clean_state"] = len(orchestrator_names) == 0
                result["actions"].append(f"Clean registry: {len(orchestrator_names)} orchestrators")
                
            logger.info("Test isolation check complete: %s", result)
            return result
            
        except Exception as e:
            result["error"] = str(e)
            result["actions"].append(f"ERROR: {e}")
            logger.error("Test isolation failed: %s", e)
            return result
    
    @staticmethod
    def verify_production_clean_state() -> bool:
        """
        Verify that production state is clean and ready for initialization.
        
        Returns:
            bool: True if clean, False if contaminated
        """
        isolation_result = TestIsolationEnforcer.reset_database_registry()
        
        return (
            isolation_result["singleton_reset"] and 
            not isolation_result["contamination_detected"] and
            isolation_result["clean_state"]
        )
    
    @staticmethod
    def get_isolation_report() -> str:
        """
        Generate human-readable test isolation report.
        
        Returns:
            str: Formatted report
        """
        result = TestIsolationEnforcer.reset_database_registry()
        
        report = [
            "🧪 CORTEX Test Isolation Report",
            "=" * 50,
            f"✅ Singleton Reset: {result['singleton_reset']}",
            f"✅ Database Cleaned: {result['database_cleaned']}",
            f"⚠️  Contamination Detected: {result['contamination_detected']}",
            f"✅ Clean State: {result['clean_state']}",
            "",
            "Actions Taken:"
        ]
        
        for action in result["actions"]:
            symbol = "❌" if "ERROR" in action or "CONTAMINATION" in action else "✅"
            report.append(f"  {symbol} {action}")
        
        if result.get("error"):
            report.extend([
                "",
                f"❌ ERROR: {result['error']}",
                "   Manual intervention required"
            ])
        
        report.append("=" * 50)
        return "\n".join(report)


class ProductionRegistryInitializer:
    """
    Safe initialization of production DatabaseBackedRegistry with test isolation.
    """
    
    @staticmethod
    def initialize_clean_registry(start_health_checker: bool = False) -> Dict[str, Any]:
        """
        Initialize production registry with guaranteed test isolation.
        
        Args:
            start_health_checker: Whether to start background health checker
            
        Returns:
            Dict with initialization results
        """
        # Step 1: Ensure clean test isolation
        if not TestIsolationEnforcer.verify_production_clean_state():
            return {
                "success": False,
                "error": "Test isolation verification failed",
                "recommendation": "Run in fresh Python process"
            }
        
        try:
            # Step 2: Use the correct production initialization pattern
            from cortex.orchestrators.core.db_wiring_init import initialize_database_wiring
            
            registry = initialize_database_wiring(start_health_checker=start_health_checker)
            
            # Step 3: Verify successful initialization
            orchestrator_count = len(registry._orchestrators)
            
            return {
                "success": True,
                "registry": registry,
                "orchestrator_count": orchestrator_count,
                "expected_count": 23,
                "health_checker": start_health_checker,
                "isolation_verified": True
            }
            
        except Exception as e:
            logger.error("Production registry initialization failed: %s", e)
            return {
                "success": False,
                "error": str(e),
                "isolation_verified": True
            }


def main():
    """Demo test isolation and clean registry initialization."""
    print(TestIsolationEnforcer.get_isolation_report())
    
    print("\n🚀 Initializing Production Registry...")
    result = ProductionRegistryInitializer.initialize_clean_registry()
    
    if result["success"]:
        print(f"✅ SUCCESS: {result['orchestrator_count']}/{result['expected_count']} orchestrators wired")
    else:
        print(f"❌ FAILED: {result['error']}")


if __name__ == "__main__":
    main()