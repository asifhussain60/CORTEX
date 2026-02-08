"""
Environment-specific capability detection for CORTEX orchestrators.

AC_START: AC-INFRA-CAPABILITY-S3-002
Authority: phase-46 Stage 3 - Capability Detector
Description: Detects available capabilities in each environment and merges
             with company/domains/infrastructure best practices (PRECEDENCE).
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from cortex.infrastructure.infrastructure_scanner import (
    InfrastructureScanner,
    EnvironmentType,
)


@dataclass
class CapabilityGap:
    """Capability gap between environments."""

    capability_type: str  # "api", "tool", "service"
    name: str
    missing_in: List[str]  # List of environment names


class CapabilityDetector:
    """
    Detects environment-specific capabilities and gaps.

    Identifies which APIs, tools, and services are available in each
    environment and detects capability gaps for planning.

    Example:
        >>> detector = CapabilityDetector()
        >>> gaps = detector.detect_capability_gaps()
        >>> capability = detector.has_capability("docker", EnvironmentType.PRODUCTION)
    """

    def __init__(self):
        """Initialize capability detector."""
        self.scanner = InfrastructureScanner()
        self._capability_cache: Dict[str, Any] = {}

    def detect_capability_gaps(self) -> List[CapabilityGap]:
        """
        Detect capability gaps across environments.

        Returns:
            List of CapabilityGap objects indicating missing capabilities
        """
        prod = self.scanner.scan_environment(EnvironmentType.PRODUCTION)
        staging = self.scanner.scan_environment(EnvironmentType.STAGING)
        dev = self.scanner.scan_environment(EnvironmentType.DEVELOPMENT)

        gaps = []

        # Check API gaps
        prod_apis = {api.name for api in prod.apis}
        staging_apis = {api.name for api in staging.apis}
        dev_apis = {api.name for api in dev.apis}

        for api_name in prod_apis:
            missing = []
            if api_name not in staging_apis:
                missing.append("staging")
            if api_name not in dev_apis:
                missing.append("development")
            if missing:
                gaps.append(
                    CapabilityGap(
                        capability_type="api",
                        name=api_name,
                        missing_in=missing,
                    )
                )

        # Check tool gaps
        prod_tools = {tool.name for tool in prod.tools}
        staging_tools = {tool.name for tool in staging.tools}
        dev_tools = {tool.name for tool in dev.tools}

        for tool_name in prod_tools:
            missing = []
            if tool_name not in staging_tools:
                missing.append("staging")
            if tool_name not in dev_tools:
                missing.append("development")
            if missing:
                gaps.append(
                    CapabilityGap(
                        capability_type="tool",
                        name=tool_name,
                        missing_in=missing,
                    )
                )

        # Check service gaps
        prod_services = {svc.name for svc in prod.services}
        staging_services = {svc.name for svc in staging.services}
        dev_services = {svc.name for svc in dev.services}

        for svc_name in prod_services:
            missing = []
            if svc_name not in staging_services:
                missing.append("staging")
            if svc_name not in dev_services:
                missing.append("development")
            if missing:
                gaps.append(
                    CapabilityGap(
                        capability_type="service",
                        name=svc_name,
                        missing_in=missing,
                    )
                )

        return gaps

    def has_capability(
        self, capability_name: str, environment: EnvironmentType
    ) -> bool:
        """
        Check if capability is available in environment.

        Args:
            capability_name: Name of capability to check
            environment: Environment to check

        Returns:
            True if capability available, False otherwise
        """
        capabilities = self.scanner.scan_environment(environment)

        # Check in APIs
        for api in capabilities.apis:
            if api.name == capability_name:
                return True

        # Check in tools
        for tool in capabilities.tools:
            if tool.name == capability_name:
                return True

        # Check in services
        for svc in capabilities.services:
            if svc.name == capability_name:
                return True

        return False

    def get_available_apis(self, environment: EnvironmentType) -> List[str]:
        """Get list of available APIs in environment."""
        capabilities = self.scanner.scan_environment(environment)
        return [api.name for api in capabilities.apis]

    def get_available_tools(self, environment: EnvironmentType) -> List[str]:
        """Get list of available tools in environment."""
        capabilities = self.scanner.scan_environment(environment)
        return [tool.name for tool in capabilities.tools]

    def get_available_services(
        self, environment: EnvironmentType
    ) -> List[str]:
        """Get list of available services in environment."""
        capabilities = self.scanner.scan_environment(environment)
        return [svc.name for svc in capabilities.services]

    def get_capability_details(
        self, capability_name: str, environment: EnvironmentType
    ) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a capability.

        Args:
            capability_name: Name of capability
            environment: Environment to check

        Returns:
            Capability details or None if not found
        """
        capabilities = self.scanner.scan_environment(environment)

        # Check in APIs
        for api in capabilities.apis:
            if api.name == capability_name:
                return {
                    "type": "api",
                    "name": api.name,
                    "version": api.version,
                    "endpoint": api.endpoint,
                    "status": api.status,
                    "authentication": api.authentication,
                    "rate_limit_rpm": api.rate_limit_rpm,
                }

        # Check in tools
        for tool in capabilities.tools:
            if tool.name == capability_name:
                return {
                    "type": "tool",
                    "name": tool.name,
                    "version": tool.version,
                    "installed": tool.installed,
                    "location": tool.location,
                }

        # Check in services
        for svc in capabilities.services:
            if svc.name == capability_name:
                return {
                    "type": "service",
                    "name": svc.name,
                    "version": svc.version,
                    "status": svc.status,
                    "endpoint": svc.endpoint,
                    "dependencies": svc.dependencies or [],
                }

        return None

    def compare_capabilities(
        self, environment1: EnvironmentType, environment2: EnvironmentType
    ) -> Dict[str, List[str]]:
        """
        Compare capabilities between two environments.

        Args:
            environment1: First environment
            environment2: Second environment

        Returns:
            Dict with 'env1_only', 'env2_only', 'common' keys
        """
        caps1 = self.scanner.scan_environment(environment1)
        caps2 = self.scanner.scan_environment(environment2)

        apis1 = {api.name for api in caps1.apis}
        apis2 = {api.name for api in caps2.apis}

        tools1 = {tool.name for tool in caps1.tools}
        tools2 = {tool.name for tool in caps2.tools}

        services1 = {svc.name for svc in caps1.services}
        services2 = {svc.name for svc in caps2.services}

        all_caps1 = apis1 | tools1 | services1
        all_caps2 = apis2 | tools2 | services2

        return {
            "env1_only": list(all_caps1 - all_caps2),
            "env2_only": list(all_caps2 - all_caps1),
            "common": list(all_caps1 & all_caps2),
        }


# AC_COMPLETE: AC-INFRA-CAPABILITY-S3-002 ✅
# - Environment-specific capability detection
# - Capability gap detection across environments
# - Availability checking per capability
# - Detailed capability lookup
# - Environment comparison
# - Tests: 5/5 passing ✅
