"""
Unit tests for security and monitoring discovery.

Task: DISC-007
Authority: PHASE-9-DISCOVERY-ORCHESTRATOR.yaml
"""

import json
import tempfile
import pytest
from pathlib import Path

from cortex.brain.discovery.security_discovery import (
    SecurityDiscovery,
    AuthProviderType,
    LoggingFramework,
)


class TestSecurityDiscoveryInit:
    """Test security discovery initialization."""
    
    def test_init_creates_discovery(self) -> None:
        """Test that discovery can be instantiated."""
        discovery = SecurityDiscovery()
        assert discovery is not None
        assert hasattr(discovery, "discover")
    
    def test_supported_features_defined(self) -> None:
        """Test that supported features are defined."""
        discovery = SecurityDiscovery()
        features = discovery.get_supported_features()
        assert len(features) > 0
        assert "authentication" in features
        assert "logging" in features


class TestAuthenticationDiscovery:
    """Test authentication provider discovery."""
    
    def test_detect_jwt_authentication(self, tmp_path: Path) -> None:
        """Test detecting JWT authentication."""
        config_file = tmp_path / "appsettings.json"
        config_file.write_text(json.dumps({
            "Authentication": {
                "JwtBearer": {
                    "Authority": "https://auth.example.com",
                    "Audience": "myapp"
                }
            }
        }))
        
        discovery = SecurityDiscovery()
        result = discovery.detect_authentication(tmp_path)
        
        assert result is not None
        assert len(result) >= 1
        assert result[0]["type"] == "jwt"
    
    def test_detect_oauth_configuration(self, tmp_path: Path) -> None:
        """Test detecting OAuth configuration."""
        env_file = tmp_path / ".env"
        env_file.write_text("""
OAUTH_CLIENT_ID=abc123
OAUTH_CLIENT_SECRET=secret
OAUTH_REDIRECT_URI=https://app.com/callback
""")
        
        discovery = SecurityDiscovery()
        result = discovery.detect_authentication(tmp_path)
        
        assert result is not None
        oauth = next((r for r in result if r["type"] == "oauth"), None)
        assert oauth is not None
    
    def test_detect_saml_configuration(self, tmp_path: Path) -> None:
        """Test detecting SAML configuration."""
        saml_file = tmp_path / "saml.xml"
        saml_file.write_text("""
<?xml version="1.0"?>
<EntityDescriptor entityID="https://idp.example.com">
  <SPSSODescriptor>
    <AssertionConsumerService />
  </SPSSODescriptor>
</EntityDescriptor>
""")
        
        discovery = SecurityDiscovery()
        result = discovery.detect_authentication(tmp_path)
        
        assert result is not None
        saml = next((r for r in result if r["type"] == "saml"), None)
        assert saml is not None


class TestAuthorizationDiscovery:
    """Test authorization policy discovery."""
    
    def test_detect_rbac_policies(self, tmp_path: Path) -> None:
        """Test detecting RBAC policies."""
        policy_file = tmp_path / "policies.py"
        policy_file.write_text("""
from functools import wraps

def require_role(role):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            # RBAC check
            return f(*args, **kwargs)
        return decorated
    return decorator

@require_role('admin')
def admin_function():
    pass
""")
        
        discovery = SecurityDiscovery()
        result = discovery.detect_authorization(tmp_path)
        
        assert result is not None
        assert result["type"] == "rbac"
    
    def test_detect_abac_policies(self, tmp_path: Path) -> None:
        """Test detecting ABAC policies."""
        policy_file = tmp_path / "authorization.yaml"
        policy_file.write_text("""
policies:
  - name: read-documents
    effect: allow
    actions:
      - read
    resources:
      - document:*
    conditions:
      department: engineering
""")
        
        discovery = SecurityDiscovery()
        result = discovery.detect_authorization(tmp_path)
        
        assert result is not None
        assert result["type"] == "abac"


class TestLoggingDiscovery:
    """Test logging framework discovery."""
    
    def test_detect_serilog(self, tmp_path: Path) -> None:
        """Test detecting Serilog."""
        program_file = tmp_path / "Program.cs"
        program_file.write_text("""
using Serilog;

Log.Logger = new LoggerConfiguration()
    .WriteTo.Console()
    .WriteTo.File("logs/app.log")
    .CreateLogger();
""")
        
        discovery = SecurityDiscovery()
        result = discovery.detect_logging(tmp_path)
        
        assert result is not None
        assert result["framework"] == "serilog"
    
    def test_detect_winston(self, tmp_path: Path) -> None:
        """Test detecting Winston."""
        logger_file = tmp_path / "logger.js"
        logger_file.write_text("""
const winston = require('winston');

const logger = winston.createLogger({
  level: 'info',
  transports: [
    new winston.transports.File({ filename: 'error.log', level: 'error' }),
    new winston.transports.Console()
  ]
});
""")
        
        discovery = SecurityDiscovery()
        result = discovery.detect_logging(tmp_path)
        
        assert result is not None
        assert result["framework"] == "winston"
    
    def test_detect_loguru(self, tmp_path: Path) -> None:
        """Test detecting Loguru."""
        logger_file = tmp_path / "logger.py"
        logger_file.write_text("""
from loguru import logger

logger.add("file.log", rotation="500 MB")
logger.info("Application started")
""")
        
        discovery = SecurityDiscovery()
        result = discovery.detect_logging(tmp_path)
        
        assert result is not None
        assert result["framework"] == "loguru"


class TestAPMDiscovery:
    """Test APM integration discovery."""
    
    def test_detect_datadog(self, tmp_path: Path) -> None:
        """Test detecting DataDog."""
        config_file = tmp_path / "datadog.yaml"
        config_file.write_text("""
api_key: abc123
app_key: def456
logs_enabled: true
apm_enabled: true
""")
        
        discovery = SecurityDiscovery()
        result = discovery.detect_apm(tmp_path)
        
        assert result is not None
        assert result["provider"] == "datadog"
    
    def test_detect_new_relic(self, tmp_path: Path) -> None:
        """Test detecting New Relic."""
        config_file = tmp_path / "newrelic.ini"
        config_file.write_text("""
[newrelic]
license_key = abc123
app_name = MyApp
""")
        
        discovery = SecurityDiscovery()
        result = discovery.detect_apm(tmp_path)
        
        assert result is not None
        assert result["provider"] == "newrelic"
    
    def test_detect_prometheus(self, tmp_path: Path) -> None:
        """Test detecting Prometheus."""
        config_file = tmp_path / "prometheus.yml"
        config_file.write_text("""
global:
  scrape_interval: 15s
scrape_configs:
  - job_name: 'myapp'
    static_configs:
      - targets: ['localhost:9090']
""")
        
        discovery = SecurityDiscovery()
        result = discovery.detect_apm(tmp_path)
        
        assert result is not None
        assert result["provider"] == "prometheus"


class TestSecurityScanningDiscovery:
    """Test security scanning tool discovery."""
    
    def test_detect_snyk(self, tmp_path: Path) -> None:
        """Test detecting Snyk."""
        snyk_file = tmp_path / ".snyk"
        snyk_file.write_text("""
version: v1.0.0
ignore: {}
""")
        
        discovery = SecurityDiscovery()
        result = discovery.detect_security_scanning(tmp_path)
        
        assert result is not None
        assert "snyk" in [s["tool"] for s in result]
    
    def test_detect_sonarqube(self, tmp_path: Path) -> None:
        """Test detecting SonarQube."""
        sonar_file = tmp_path / "sonar-project.properties"
        sonar_file.write_text("""
sonar.projectKey=myproject
sonar.sources=src
sonar.exclusions=**/test/**
""")
        
        discovery = SecurityDiscovery()
        result = discovery.detect_security_scanning(tmp_path)
        
        assert result is not None
        assert "sonarqube" in [s["tool"] for s in result]


class TestFullSecurityDiscovery:
    """Test complete security discovery."""
    
    def test_discover_complete_security_setup(self, tmp_path: Path) -> None:
        """Test discovering complete security configuration."""
        # Create JWT config
        (tmp_path / "appsettings.json").write_text(json.dumps({
            "Authentication": {"JwtBearer": {"Authority": "https://auth.com"}}
        }))
        
        # Create logging
        (tmp_path / "logger.py").write_text("from loguru import logger")
        
        # Create APM
        (tmp_path / "prometheus.yml").write_text("global:\n  scrape_interval: 15s")
        
        discovery = SecurityDiscovery()
        result = discovery.discover(tmp_path)
        
        assert result is not None
        assert len(result["authentication"]) >= 1
        assert result["logging"] is not None
        assert result["apm"] is not None
    
    def test_discover_handles_no_security(self, tmp_path: Path) -> None:
        """Test discovery with no security configuration."""
        discovery = SecurityDiscovery()
        result = discovery.discover(tmp_path)
        
        assert result is not None
        assert len(result["authentication"]) == 0
