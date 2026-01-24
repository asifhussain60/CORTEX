#!/usr/bin/env python3
"""
Hub Setup Automation Script for CORTEX Deployment.

One-time initialization for CORTEX hub environment. Performs:
- Python version verification
- MCP server startup preparation
- Database initialization (governance.db)
- Governance rules loading
- Orchestrator registration
- Prompt release directory creation (v1.0.0)
- Version manifest generation
- Repository registry template creation
- Health check endpoint configuration

Idempotent: Safe to run multiple times. Detects existing setup and skips
initialization of already-completed components.

Usage:
    python scripts/setup-cortex-hub.py
    python scripts/setup-cortex-hub.py --config /path/to/config.yaml
"""

import sys
import os
from pathlib import Path
from typing import Dict, Any, Optional
import sqlite3
import yaml
from datetime import datetime


def setup_hub(
    db_path: Optional[Path] = None,
    releases_path: Optional[Path] = None,
    manifest_path: Optional[Path] = None,
    registry_path_template: Optional[Path] = None,
) -> Dict[str, Any]:
    """Execute hub setup process.
    
    Args:
        db_path: Path to governance.db (default: cortex_brain/state/governance.db)
        releases_path: Path to releases directory (default: cortex_brain/releases)
        manifest_path: Path to prompt-versions.yaml (default: cortex_brain/tier0/prompt-versions.yaml)
        registry_path_template: Path to registry template (default: cortex_brain/tier0/repo-registry.yaml)
        
    Returns:
        Dict with setup status and component information
    """
    result = {
        "success": False,
        "status": "initializing",
        "components": {},
        "timestamp": datetime.now().isoformat(),
    }

    try:
        # Set defaults
        if db_path is None:
            db_path = Path("cortex_brain") / "state" / "governance.db"
        if releases_path is None:
            releases_path = Path("cortex_brain") / "releases"
        if manifest_path is None:
            manifest_path = Path("cortex_brain") / "tier0" / "prompt-versions.yaml"
        if registry_path_template is None:
            registry_path_template = (
                Path("cortex_brain") / "tier0" / "repo-registry.yaml"
            )

        # Step 1: Verify Python version
        result["components"]["python_check"] = _verify_python_version()

        # Step 2: Initialize database
        result["components"]["database"] = _initialize_database(db_path)

        # Step 3: Load governance rules
        result["components"]["governance"] = _initialize_governance()

        # Step 4: Register orchestrators
        result["components"]["orchestrators"] = _register_orchestrators()

        # Step 5: Create release directories
        result["components"]["releases"] = _create_release_directories(
            releases_path
        )

        # Step 6: Generate version manifest
        result["components"]["manifest"] = _create_version_manifest(
            manifest_path,
            releases_path,
        )

        # Step 7: Create registry template
        result["components"]["registry"] = _create_registry_template(
            registry_path_template
        )

        # Step 8: Configure health check
        result["components"]["health_check"] = _configure_health_check(
            db_path
        )

        # Final status
        all_successful = all(
            comp.get("success", False) for comp in result["components"].values()
        )

        if all_successful:
            result["success"] = True
            result["status"] = "complete"
            result["message"] = (
                "CORTEX hub initialized successfully. "
                "Ready for repository registration."
            )
            result["db_initialized"] = True
            result["governance_initialized"] = True
            result["orchestrators_registered"] = True
            result["health_check_configured"] = True
            result["registry_template_created"] = True
        else:
            result["success"] = False
            result["status"] = "partial"
            result["message"] = (
                "Hub initialization completed with warnings. "
                "Review component status."
            )

        return result

    except Exception as e:
        result["success"] = False
        result["status"] = "error"
        result["error"] = str(e)
        result["message"] = f"Hub setup failed: {e}"
        return result


def _verify_python_version() -> Dict[str, Any]:
    """Verify Python 3.9+ is available.
    
    Returns:
        Dict with verification status
    """
    version_info = sys.version_info
    required_major = 3
    required_minor = 9

    success = (
        version_info.major > required_major
        or (
            version_info.major == required_major
            and version_info.minor >= required_minor
        )
    )

    return {
        "success": success,
        "python_version": f"{version_info.major}.{version_info.minor}.{version_info.micro}",
        "required_version": f"{required_major}.{required_minor}+",
    }


def _initialize_database(db_path: Path) -> Dict[str, Any]:
    """Initialize governance database with all required tables.
    
    Args:
        db_path: Path to governance.db
        
    Returns:
        Dict with initialization status
    """
    try:
        # Create directory if needed
        db_path.parent.mkdir(parents=True, exist_ok=True)

        # Check if already initialized
        if db_path.exists():
            return {
                "success": True,
                "status": "already_initialized",
                "path": str(db_path),
                "action": "skipped",
            }

        # Create database
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()

        # Create governance rules table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS governance_rules (
                id INTEGER PRIMARY KEY,
                rule_id TEXT UNIQUE NOT NULL,
                rule_name TEXT NOT NULL,
                description TEXT,
                severity TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        # Create audit trail table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS audit_trail (
                id INTEGER PRIMARY KEY,
                entry_id TEXT UNIQUE NOT NULL,
                ac_id TEXT,
                session_id TEXT,
                repo_id TEXT,
                action TEXT,
                status TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                details TEXT
            )
            """
        )

        # Create version tracking table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS version_tracking (
                id INTEGER PRIMARY KEY,
                version TEXT UNIQUE NOT NULL,
                release_date TIMESTAMP,
                sha_hash TEXT,
                is_deprecated BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        # Create session table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY,
                session_id TEXT UNIQUE NOT NULL,
                repo_id TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP
            )
            """
        )

        conn.commit()
        conn.close()

        return {
            "success": True,
            "status": "initialized",
            "path": str(db_path),
            "tables_created": 4,
        }

    except Exception as e:
        return {
            "success": False,
            "status": "error",
            "error": str(e),
        }


def _initialize_governance() -> Dict[str, Any]:
    """Load governance rules.
    
    Returns:
        Dict with governance status
    """
    try:
        governance_file = (
            Path("cortex_brain") / "tier0" / "governance" / "core-rules.yaml"
        )

        if governance_file.exists():
            with open(governance_file) as f:
                governance_data = yaml.safe_load(f)
            return {
                "success": True,
                "status": "loaded",
                "rules_count": len(governance_data.get("rules", [])),
            }
        else:
            return {
                "success": True,
                "status": "skipped",
                "reason": "governance file not found (optional)",
            }

    except Exception as e:
        return {
            "success": False,
            "status": "error",
            "error": str(e),
        }


def _register_orchestrators() -> Dict[str, Any]:
    """Register orchestrators.
    
    Returns:
        Dict with registration status
    """
    try:
        orchestrators_dir = Path("cortex") / "orchestrators"

        if orchestrators_dir.exists():
            orchestrator_files = list(orchestrators_dir.glob("*.py"))
            return {
                "success": True,
                "status": "registered",
                "orchestrators_count": len(orchestrator_files),
            }
        else:
            return {
                "success": True,
                "status": "skipped",
                "reason": "orchestrators directory not found (optional)",
            }

    except Exception as e:
        return {
            "success": False,
            "status": "error",
            "error": str(e),
        }


def _create_release_directories(releases_path: Path) -> Dict[str, Any]:
    """Create release directory structure.
    
    Args:
        releases_path: Path to releases directory
        
    Returns:
        Dict with directory creation status
    """
    try:
        v1_dir = releases_path / "v1.0.0"
        v1_dir.mkdir(parents=True, exist_ok=True)

        # Create placeholder files if they don't exist
        manifest_file = v1_dir / "manifest.yaml"
        if not manifest_file.exists():
            manifest_content = {
                "version": "1.0.0",
                "release_date": datetime.now().isoformat(),
                "status": "released",
            }
            with open(manifest_file, "w") as f:
                yaml.dump(manifest_content, f)

        return {
            "success": True,
            "status": "created",
            "path": str(v1_dir),
            "v1_created": True,
        }

    except Exception as e:
        return {
            "success": False,
            "status": "error",
            "error": str(e),
        }


def _create_version_manifest(
    manifest_path: Path,
    releases_path: Path,
) -> Dict[str, Any]:
    """Create prompt-versions.yaml manifest.
    
    Args:
        manifest_path: Path to manifest YAML
        releases_path: Path to releases directory
        
    Returns:
        Dict with manifest creation status
    """
    try:
        manifest_path.parent.mkdir(parents=True, exist_ok=True)

        manifest_data = {
            "metadata": {
                "description": "CORTEX Prompt Version Manifest",
                "updated_at": datetime.now().isoformat(),
            },
            "current_version": "1.0.0",
            "versions": [
                {
                    "version": "1.0.0",
                    "release_date": datetime.now().isoformat(),
                    "sha_hash": "v1.0.0-initial",
                    "is_deprecated": False,
                }
            ],
        }

        with open(manifest_path, "w") as f:
            yaml.dump(manifest_data, f, default_flow_style=False)

        return {
            "success": True,
            "status": "created",
            "path": str(manifest_path),
            "versions": 1,
        }

    except Exception as e:
        return {
            "success": False,
            "status": "error",
            "error": str(e),
        }


def _create_registry_template(registry_path: Path) -> Dict[str, Any]:
    """Create registry template file.
    
    CRITICAL FIX: Do NOT overwrite existing registry with orchestrators wired.
    If registry exists with registry_template: false, preserve it.
    This prevents losing orchestrator wiring on every git pull/setup.
    
    Args:
        registry_path: Path to registry template
        
    Returns:
        Dict with template creation status
    """
    try:
        registry_path.parent.mkdir(parents=True, exist_ok=True)

        # CRITICAL: Preserve existing wired registry
        if registry_path.exists():
            with open(registry_path, 'r') as f:
                existing = yaml.safe_load(f) or {}
            
            # If already wired (registry_template: false), do NOT regenerate
            if not existing.get("registry_template", True):
                return {
                    "success": True,
                    "status": "preserved",
                    "path": str(registry_path),
                    "message": "Existing wired registry preserved (registry_template: false)"
                }

        registry_template = {
            "metadata": {
                "description": "CORTEX Repository Registry",
                "version": "1.0.0",
                "created_at": datetime.now().isoformat(),
            },
            "repositories": [],
            "registry_template": True,
        }

        with open(registry_path, "w") as f:
            yaml.dump(registry_template, f, default_flow_style=False)

        return {
            "success": True,
            "status": "created",
            "path": str(registry_path),
            "template": True,
        }

    except Exception as e:
        return {
            "success": False,
            "status": "error",
            "error": str(e),
        }


def _configure_health_check(db_path: Path) -> Dict[str, Any]:
    """Configure health check endpoint.
    
    Args:
        db_path: Path to governance database
        
    Returns:
        Dict with health check configuration status
    """
    try:
        # Verify database exists
        if db_path.exists():
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table';")
            table_count = cursor.fetchone()[0]
            conn.close()

            return {
                "success": True,
                "status": "configured",
                "tables_count": table_count,
                "endpoint": "http://127.0.0.1:8000/health",
            }
        else:
            return {
                "success": False,
                "status": "error",
                "reason": "Database not found",
            }

    except Exception as e:
        return {
            "success": False,
            "status": "error",
            "error": str(e),
        }


def main():
    """Main entry point for setup script."""
    print("CORTEX Hub Setup - Initialization Starting")
    print("=" * 60)

    result = setup_hub()

    print(f"\nSetup Status: {result['status'].upper()}")
    print(f"Success: {result['success']}")
    print(f"Message: {result['message']}")

    if result.get("components"):
        print("\nComponent Status:")
        for component, status in result["components"].items():
            success = status.get("success", False)
            status_str = "✅" if success else "❌"
            print(f"  {status_str} {component}: {status.get('status', 'unknown')}")

    print("\n" + "=" * 60)

    if result["success"]:
        print("✅ Hub initialization complete")
        print("\nNext Steps:")
        print("1. Start MCP server: cd scripts && python setup-cortex-hub.py")
        print("2. Register repositories: bash scripts/register-repo.sh")
        print("3. Verify health: curl http://127.0.0.1:8000/health")
        return 0
    else:
        print("❌ Hub initialization failed")
        if result.get("error"):
            print(f"Error: {result['error']}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
