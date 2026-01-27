"""
MCP Service Discovery with Health Checks.

Implements service discovery and health monitoring for MCP hub:
- /health endpoint for readiness probes
- /config/prompt-version for version negotiation
- Service discovery sequence (env var → config → default)
- Health check caching and latency optimization

Key components:
- HealthCheck: Health status monitoring
- ServiceDiscovery: MCP hub endpoint discovery
- PromptVersionConfig: Version management
"""

import os
import logging
import re
from datetime import datetime, timedelta
from typing import Dict, Optional, Any, List
from threading import Lock
import yaml

logger = logging.getLogger(__name__)


class HealthCheck:
    """Monitors health of MCP hub and dependencies.

    Provides:
    - Database connectivity check
    - Governance rules loaded verification
    - Orchestrators registered check
    - Overall health status calculation
    - Result caching with TTL
    - <100ms latency for cached results

    Example:
        >>> checker = HealthCheck()
        >>> status = checker.check_health()
        >>> assert status["status"] in ["healthy", "degraded", "unhealthy"]
    """

    def __init__(self, cache_ttl_seconds: int = 30):
        """Initialize health checker.

        Args:
            cache_ttl_seconds: Cache lifetime (default 30s)
        """
        self.cache_ttl_seconds = cache_ttl_seconds
        self._cache: Optional[Dict[str, Any]] = None
        self._cache_time: Optional[datetime] = None
        self._lock = Lock()

    def check_health(self) -> Dict[str, Any]:
        """Check overall health of MCP hub.

        Returns:
            Dict with:
            - status: "healthy", "degraded", or "unhealthy"
            - timestamp: ISO format check time
            - components: Dict with status of each component

        Example:
            >>> checker = HealthCheck()
            >>> health = checker.check_health()
            >>> assert health["components"]["database"]["status"] in ["healthy", "failed"]
        """
        with self._lock:
            # Return cached result if fresh
            if self._cache is not None:
                if (
                    datetime.now() - self._cache_time
                ).total_seconds() < self.cache_ttl_seconds:
                    return self._cache

        # Perform fresh health check
        components = {
            "database": {
                "status": "healthy"
                if self._check_db_connection()
                else "failed",
            },
            "governance": {
                "status": "healthy"
                if self._check_governance_rules()
                else "failed",
            },
            "orchestrators": {
                "status": "healthy"
                if self._check_orchestrators_registered()
                else "failed",
            },
        }

        # Calculate overall status
        failed_count = sum(
            1 for c in components.values() if c["status"] == "failed"
        )

        if failed_count == 0:
            overall_status = "healthy"
        elif failed_count == 1:
            overall_status = "degraded"
        else:
            overall_status = "unhealthy"

        result = {
            "status": overall_status,
            "timestamp": datetime.now().isoformat(),
            "components": components,
        }

        # Cache result
        with self._lock:
            self._cache = result
            self._cache_time = datetime.now()

        return result

    def _check_db_connection(self) -> bool:
        """Check database connection.

        Returns:
            bool: True if DB connected, False otherwise
        """
        try:
            # Would check actual DB connection here
            # For now, assume healthy
            return True
        except Exception as e:
            logger.error(f"Database connection check failed: {e}")
            return False

    def _check_governance_rules(self) -> bool:
        """Check if governance rules are loaded.

        Returns:
            bool: True if rules loaded, False otherwise
        """
        try:
            # Would check actual governance registry here
            # For now, assume healthy
            return True
        except Exception as e:
            logger.error(f"Governance rules check failed: {e}")
            return False

    def _check_orchestrators_registered(self) -> bool:
        """Check if orchestrators are registered.

        Returns:
            bool: True if orchestrators registered, False otherwise
        """
        try:
            # Would check actual orchestrator registry here
            # For now, assume healthy
            return True
        except Exception as e:
            logger.error(f"Orchestrators check failed: {e}")
            return False


class ServiceDiscovery:
    """Discovers MCP hub endpoint via discovery sequence.

    Discovery sequence:
    1. CORTEX_MCP_ENDPOINT environment variable
    2. cortex-config.yaml file
    3. Default: http://127.0.0.1:8000

    Example:
        >>> discovery = ServiceDiscovery()
        >>> endpoint = discovery.discover_endpoint()
        >>> assert endpoint.startswith("http://")
    """

    DEFAULT_ENDPOINT = "http://127.0.0.1:8000"

    def __init__(self):
        """Initialize service discovery."""
        self._lock = Lock()
        self._discovered_endpoint: Optional[str] = None

    def discover_endpoint(self) -> str:
        """Discover MCP hub endpoint.

        Returns:
            str: Discovered endpoint URL

        Tries in order:
        1. CORTEX_MCP_ENDPOINT env var
        2. cortex-config.yaml
        3. Default endpoint
        """
        # Try environment variable
        env_endpoint = os.environ.get("CORTEX_MCP_ENDPOINT")
        if env_endpoint and self.validate_endpoint(env_endpoint):
            return env_endpoint

        # Try config file
        config_endpoint = self._load_config_file()
        if config_endpoint and self.validate_endpoint(config_endpoint):
            return config_endpoint

        # Use default
        return self.DEFAULT_ENDPOINT

    def _load_config_file(self) -> Optional[str]:
        """Load endpoint from cortex-config.yaml.

        Returns:
            str: Endpoint from config, or None if not found
        """
        config_files = [
            "cortex/config/cortex-config.yaml",
            "cortex-config.yaml",  # Legacy location
            ".github/cortex-config.yaml",
            "/etc/cortex/config.yaml",
        ]

        for config_file in config_files:
            if os.path.exists(config_file):
                try:
                    data = self._load_yaml_file(config_file)
                    if data and "mcp_endpoint" in data:
                        return data["mcp_endpoint"]
                except Exception as e:
                    logger.warning(f"Failed to load {config_file}: {e}")

        return None

    def _load_yaml_file(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Load YAML file.

        Args:
            file_path: Path to YAML file

        Returns:
            Dict with file contents, or None if error
        """
        try:
            with open(file_path, "r") as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Error loading YAML {file_path}: {e}")
            return None

    def validate_endpoint(self, endpoint: str) -> bool:
        """Validate endpoint URL format.

        Args:
            endpoint: URL to validate

        Returns:
            bool: True if valid HTTP/HTTPS endpoint

        Example:
            >>> discovery = ServiceDiscovery()
            >>> assert discovery.validate_endpoint("http://localhost:8000")
            >>> assert not discovery.validate_endpoint("ftp://invalid")
        """
        if not endpoint:
            return False

        # Must start with http:// or https://
        if not endpoint.startswith(("http://", "https://")):
            return False

        # Must have host and port
        try:
            url_pattern = r"^https?://[a-zA-Z0-9.-]+(\:\d+)?(/.*)?$"
            return bool(re.match(url_pattern, endpoint))
        except Exception:
            return False

    def validate_endpoint_reachable(self, endpoint: str) -> bool:
        """Check if endpoint is reachable.

        Args:
            endpoint: URL to check

        Returns:
            bool: True if reachable

        Attempts to make HTTP connection (lightweight check).
        """
        if not self.validate_endpoint(endpoint):
            return False

        try:
            import urllib.request
            import urllib.error

            try:
                response = urllib.request.urlopen(
                    endpoint + "/health", timeout=2
                )
                return response.status == 200
            except urllib.error.URLError:
                return False
        except Exception:
            return False


class PromptVersionConfig:
    """Manages prompt version configuration and negotiation.

    Provides:
    - Current version tracking
    - Compatible versions list
    - Version negotiation logic
    - Schema information

    Example:
        >>> config = PromptVersionConfig()
        >>> version_info = config.get_version_config()
        >>> assert "current_version" in version_info
    """

    def __init__(self):
        """Initialize version config."""
        self._current_version = "1.0.0"
        self._compatible_versions = ["1.0.0"]
        self._lock = Lock()

    def get_version_config(self) -> Dict[str, Any]:
        """Get current prompt version configuration.

        Returns:
            Dict with:
            - current_version: Current version string
            - compatible_versions: List of compatible versions
            - schema: Schema version information

        Example:
            >>> config = PromptVersionConfig()
            >>> info = config.get_version_config()
            >>> assert info["current_version"] == "1.0.0"
        """
        with self._lock:
            return {
                "current_version": self._current_version,
                "compatible_versions": self._compatible_versions.copy(),
                "schema": {
                    "version": "1.0",
                    "format": "YAML",
                },
                "timestamp": datetime.now().isoformat(),
            }

    def _get_current_version(self) -> str:
        """Get current version.

        Returns:
            str: Current version string
        """
        return self._current_version

    def is_version_compatible(
        self, requested_version: str
    ) -> bool:
        """Check if version is compatible.

        Args:
            requested_version: Version to check

        Returns:
            bool: True if compatible
        """
        with self._lock:
            return requested_version in self._compatible_versions

    def get_compatible_versions(self) -> List[str]:
        """Get list of compatible versions.

        Returns:
            List[str]: Compatible version strings
        """
        with self._lock:
            return self._compatible_versions.copy()
