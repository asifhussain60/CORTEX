"""
Security and Monitoring Discovery

Discovers authentication providers, authorization policies, logging frameworks,
APM integrations, and security scanning tools.

Supports:
- Authentication (JWT, OAuth, SAML, API keys)
- Authorization (RBAC, ABAC)
- Logging (Serilog, Winston, Loguru, Python logging)
- APM (DataDog, New Relic, Prometheus)
- Security scanning (Snyk, SonarQube)

Task: DISC-007
Authority: PHASE-9-DISCOVERY-ORCHESTRATOR.yaml
Governance: CORE-008, CORE-011, CORE-012, CORE-030
"""

import json
import logging
import re
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from cortex.brain.discovery import DiscoveryPlugin

logger = logging.getLogger(__name__)


class AuthProviderType(Enum):
    """
    Authentication provider types.

    Attributes:
        JWT: JSON Web Token
        OAUTH: OAuth 2.0
        SAML: SAML 2.0
        API_KEY: API key authentication
    """
    JWT = "jwt"
    OAUTH = "oauth"
    SAML = "saml"
    API_KEY = "api_key"


class LoggingFramework(Enum):
    """
    Logging framework types.

    Attributes:
        SERILOG: Serilog (C#)
        WINSTON: Winston (Node.js)
        LOGURU: Loguru (Python)
        PYTHON_LOGGING: Python logging module
    """
    SERILOG = "serilog"
    WINSTON = "winston"
    LOGURU = "loguru"
    PYTHON_LOGGING = "python_logging"


class SecurityDiscovery(DiscoveryPlugin):
    """
    Discovers security and monitoring configurations.

    Analyzes authentication providers, authorization policies,
    logging frameworks, APM integrations, and security scanning tools.

    Features:
    - Multi-auth provider support (JWT, OAuth, SAML)
    - Authorization policy detection (RBAC, ABAC)
    - Logging framework discovery
    - APM integration detection
    - Security scanning tool discovery

    Example:
        ```python
        discovery = SecurityDiscovery()
        topology = discovery.discover(Path("/my/repo"))

        for auth in topology["authentication"]:
            print(f"Auth provider: {auth['type']}")
        ```
    """

    def __init__(self) -> None:
        """Initialize security discovery."""
        self.supported_features = ["authentication", "authorization", "logging", "apm", "security_scanning"]
        logger.info("SecurityDiscovery initialized")

    def get_supported_features(self) -> List[str]:
        """
        Get list of supported security features.

        Returns:
            List of feature names
        """
        return self.supported_features

    def discover(self, repo_path: Path) -> Dict[str, Any]:
        """
        Discover security and monitoring topology in repository.

        Args:
            repo_path: Path to repository to scan

        Returns:
            Dictionary containing security topology
        """
        logger.info(f"Discovering security topology in {repo_path}")

        authentication = self.detect_authentication(repo_path)
        authorization = self.detect_authorization(repo_path)
        logging_config = self.detect_logging(repo_path)
        apm_config = self.detect_apm(repo_path)
        security_scanning = self.detect_security_scanning(repo_path)

        logger.info(
            f"Discovered {len(authentication)} auth providers, "
            f"logging: {logging_config['framework'] if logging_config else 'none'}, "
            f"APM: {apm_config['provider'] if apm_config else 'none'}"
        )

        return {
            "authentication": authentication,
            "authorization": authorization,
            "logging": logging_config,
            "apm": apm_config,
            "security_scanning": security_scanning,
            "total_auth_providers": len(authentication),
            "total_security_tools": len(security_scanning) if security_scanning else 0,
        }

    def detect_authentication(self, repo_path: Path) -> List[Dict[str, Any]]:
        """
        Detect authentication providers.

        Args:
            repo_path: Path to repository

        Returns:
            List of authentication providers
        """
        providers = []

        # Check for JWT
        for config_file in repo_path.rglob("appsettings*.json"):
            try:
                with open(config_file) as f:
                    config = json.load(f)
                    if "Authentication" in config:
                        if "JwtBearer" in config["Authentication"]:
                            providers.append({
                                "type": "jwt",
                                "config_file": str(config_file),
                            })
            except Exception as e:
                logger.debug(f"Error reading auth config from {config_file}: {e}")

        # Check for OAuth
        for env_file in repo_path.rglob(".env*"):
            try:
                content = env_file.read_text()
                if "OAUTH_CLIENT_ID" in content or "OAUTH_CLIENT_SECRET" in content:
                    providers.append({
                        "type": "oauth",
                        "config_file": str(env_file),
                    })
            except Exception as e:
                logger.debug(f"Error reading OAuth config from {env_file}: {e}")

        # Check for SAML
        for saml_file in repo_path.rglob("*.xml"):
            if "saml" in saml_file.name.lower():
                try:
                    content = saml_file.read_text()
                    if "EntityDescriptor" in content or "SAML" in content:
                        providers.append({
                            "type": "saml",
                            "config_file": str(saml_file),
                        })
                except Exception as e:
                    logger.debug(f"Error reading SAML config from {saml_file}: {e}")

        logger.debug(f"Detected {len(providers)} authentication providers")
        return providers

    def detect_authorization(self, repo_path: Path) -> Optional[Dict[str, Any]]:
        """
        Detect authorization policies.

        Args:
            repo_path: Path to repository

        Returns:
            Authorization policy information or None
        """
        # Check for RBAC
        for py_file in repo_path.rglob("*.py"):
            try:
                content = py_file.read_text()
                if "require_role" in content or "@role" in content:
                    logger.debug(f"Detected RBAC in {py_file}")
                    return {
                        "type": "rbac",
                        "files": [str(py_file)],
                    }
            except Exception:
                pass

        # Check for ABAC
        for policy_file in repo_path.rglob("*authorization*.yaml"):
            try:
                with open(policy_file) as f:
                    config = yaml.safe_load(f)
                    if config and "policies" in config:
                        logger.debug(f"Detected ABAC in {policy_file}")
                        return {
                            "type": "abac",
                            "config_file": str(policy_file),
                        }
            except Exception:
                pass

        return None

    def detect_logging(self, repo_path: Path) -> Optional[Dict[str, Any]]:
        """
        Detect logging framework.

        Args:
            repo_path: Path to repository

        Returns:
            Logging framework information or None
        """
        # Check for Serilog
        for cs_file in repo_path.rglob("*.cs"):
            try:
                content = cs_file.read_text()
                if "using Serilog" in content:
                    logger.debug(f"Detected Serilog in {cs_file}")
                    return {
                        "framework": "serilog",
                        "file": str(cs_file),
                    }
            except Exception:
                pass

        # Check for Winston
        for js_file in repo_path.rglob("*.js"):
            try:
                content = js_file.read_text()
                if "winston" in content and "createLogger" in content:
                    logger.debug(f"Detected Winston in {js_file}")
                    return {
                        "framework": "winston",
                        "file": str(js_file),
                    }
            except Exception:
                pass

        # Check for Loguru
        for py_file in repo_path.rglob("*.py"):
            try:
                content = py_file.read_text()
                if "from loguru import logger" in content:
                    logger.debug(f"Detected Loguru in {py_file}")
                    return {
                        "framework": "loguru",
                        "file": str(py_file),
                    }
            except Exception:
                pass

        return None

    def detect_apm(self, repo_path: Path) -> Optional[Dict[str, Any]]:
        """
        Detect APM integration.

        Args:
            repo_path: Path to repository

        Returns:
            APM provider information or None
        """
        # Check for DataDog
        datadog_config = repo_path / "datadog.yaml"
        if datadog_config.exists():
            logger.debug(f"Detected DataDog: {datadog_config}")
            return {
                "provider": "datadog",
                "config_file": str(datadog_config),
            }

        # Check for New Relic
        newrelic_config = repo_path / "newrelic.ini"
        if newrelic_config.exists():
            logger.debug(f"Detected New Relic: {newrelic_config}")
            return {
                "provider": "newrelic",
                "config_file": str(newrelic_config),
            }

        # Check for Prometheus
        for prometheus_file in repo_path.rglob("prometheus*.yml"):
            logger.debug(f"Detected Prometheus: {prometheus_file}")
            return {
                "provider": "prometheus",
                "config_file": str(prometheus_file),
            }

        for prometheus_file in repo_path.rglob("prometheus*.yaml"):
            logger.debug(f"Detected Prometheus: {prometheus_file}")
            return {
                "provider": "prometheus",
                "config_file": str(prometheus_file),
            }

        return None

    def detect_security_scanning(self, repo_path: Path) -> List[Dict[str, Any]]:
        """
        Detect security scanning tools.

        Args:
            repo_path: Path to repository

        Returns:
            List of security scanning tools
        """
        tools = []

        # Check for Snyk
        snyk_file = repo_path / ".snyk"
        if snyk_file.exists():
            tools.append({
                "tool": "snyk",
                "config_file": str(snyk_file),
            })

        # Check for SonarQube
        sonar_file = repo_path / "sonar-project.properties"
        if sonar_file.exists():
            tools.append({
                "tool": "sonarqube",
                "config_file": str(sonar_file),
            })

        logger.debug(f"Detected {len(tools)} security scanning tools")
        return tools
