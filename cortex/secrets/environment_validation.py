"""
Environment Validation Module - Phase 76 Stage 3

Validates environment variables including secrets, URLs, ports, and ranges.

Authority: phase-76-production-foundation-trilogy.yaml S3.T3
AC-ID: AC-PHASE76-S3-003
"""

import os
import logging
from typing import Dict, Any, List, Optional, Callable
from pathlib import Path
from urllib.parse import urlparse
import socket

from cortex.secrets.errors import SecretsError

logger = logging.getLogger(__name__)


class EnvironmentValidator:
    """
    Validates environment variables with type and range checks.
    
    Supported validations:
    - Required: must exist
    - Type: string, int, bool, url, port, path
    - Range: numeric bounds (min/max)
    - Custom: user-defined validator functions
    """
    
    def __init__(self):
        """Initialize validator."""
        self.validators: Dict[str, Callable] = {}
        self.required_vars: List[str] = []
        self.schema: Dict[str, Dict[str, Any]] = {}
    
    def add_required(self, var_name: str) -> "EnvironmentValidator":
        """
        Mark variable as required.
        
        Args:
            var_name: Environment variable name
            
        Returns:
            self for chaining
        """
        self.required_vars.append(var_name)
        return self
    
    def add_schema(
        self,
        var_name: str,
        var_type: str = "string",
        required: bool = False,
        default: Optional[Any] = None,
        validator: Optional[Callable] = None,
        **kwargs,
    ) -> "EnvironmentValidator":
        """
        Add variable to schema.
        
        Args:
            var_name: Variable name
            var_type: Type (string, int, bool, url, port, path, float)
            required: Must be set
            default: Default value if not set
            validator: Custom validator function
            **kwargs: Type-specific options (min, max, pattern, etc.)
            
        Returns:
            self for chaining
        """
        self.schema[var_name] = {
            "type": var_type,
            "required": required,
            "default": default,
            "validator": validator,
            "options": kwargs,
        }
        
        if required:
            self.add_required(var_name)
        
        return self
    
    def validate_all(self) -> Dict[str, Any]:
        """
        Validate all schema variables.
        
        Returns:
            Dict with "valid", "errors", "warnings", "values"
            
        Raises:
            SecretsError: If required variables missing
        """
        errors = []
        warnings = []
        values = {}
        
        # Check required variables
        for var_name in self.required_vars:
            if var_name not in os.environ:
                errors.append(f"Required variable not set: {var_name}")
        
        # Validate schema
        for var_name, schema in self.schema.items():
            result = self.validate_var(var_name, schema)
            
            if result["valid"]:
                values[var_name] = result["value"]
            elif schema.get("required"):
                errors.append(f"{var_name}: {result.get('error', 'Invalid')}")
            else:
                warnings.append(f"{var_name}: {result.get('error', 'Invalid')}")
        
        # Raise if errors
        if errors:
            error_msg = "\n".join(errors)
            raise SecretsError(f"Environment validation failed:\n{error_msg}")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "values": values,
        }
    
    def validate_var(
        self,
        var_name: str,
        schema: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Validate single variable.
        
        Args:
            var_name: Variable name
            schema: Validation schema (uses self.schema[var_name] if None)
            
        Returns:
            Dict with "valid", "value", "error"
        """
        if schema is None:
            schema = self.schema.get(var_name, {})
        
        # Get value
        value = os.getenv(var_name)
        
        # Check required
        if value is None:
            if schema.get("required"):
                return {
                    "valid": False,
                    "value": None,
                    "error": f"Required but not set",
                }
            else:
                # Use default
                default = schema.get("default")
                return {
                    "valid": True,
                    "value": default,
                    "error": None,
                }
        
        # Run custom validator first
        custom_validator = schema.get("validator")
        if custom_validator:
            try:
                if not custom_validator(value):
                    return {
                        "valid": False,
                        "value": value,
                        "error": "Custom validation failed",
                    }
            except Exception as e:
                return {
                    "valid": False,
                    "value": value,
                    "error": f"Custom validator error: {e}",
                }
        
        # Type validation
        var_type = schema.get("type", "string")
        options = schema.get("options", {})
        
        try:
            if var_type == "string":
                result = self._validate_string(value, **options)
            elif var_type == "int":
                result = self._validate_int(value, **options)
            elif var_type == "float":
                result = self._validate_float(value, **options)
            elif var_type == "bool":
                result = self._validate_bool(value, **options)
            elif var_type == "url":
                result = self._validate_url(value, **options)
            elif var_type == "port":
                result = self._validate_port(value, **options)
            elif var_type == "path":
                result = self._validate_path(value, **options)
            else:
                result = {
                    "valid": False,
                    "value": value,
                    "error": f"Unknown type: {var_type}",
                }
            
            return result
        
        except Exception as e:
            return {
                "valid": False,
                "value": value,
                "error": f"Type validation error: {e}",
            }
    
    @staticmethod
    def _validate_string(value: str, **options) -> Dict[str, Any]:
        """Validate string type."""
        min_len = options.get("min_length", 0)
        max_len = options.get("max_length")
        pattern = options.get("pattern")
        
        if len(value) < min_len:
            return {
                "valid": False,
                "value": value,
                "error": f"String shorter than {min_len} chars",
            }
        
        if max_len and len(value) > max_len:
            return {
                "valid": False,
                "value": value,
                "error": f"String longer than {max_len} chars",
            }
        
        if pattern:
            import re
            if not re.match(pattern, value):
                return {
                    "valid": False,
                    "value": value,
                    "error": f"String doesn't match pattern {pattern}",
                }
        
        return {"valid": True, "value": value, "error": None}
    
    @staticmethod
    def _validate_int(value: str, **options) -> Dict[str, Any]:
        """Validate integer type."""
        try:
            int_value = int(value)
        except ValueError:
            return {
                "valid": False,
                "value": value,
                "error": "Not a valid integer",
            }
        
        min_val = options.get("min")
        max_val = options.get("max")
        
        if min_val is not None and int_value < min_val:
            return {
                "valid": False,
                "value": int_value,
                "error": f"Value less than minimum {min_val}",
            }
        
        if max_val is not None and int_value > max_val:
            return {
                "valid": False,
                "value": int_value,
                "error": f"Value greater than maximum {max_val}",
            }
        
        return {"valid": True, "value": int_value, "error": None}
    
    @staticmethod
    def _validate_float(value: str, **options) -> Dict[str, Any]:
        """Validate float type."""
        try:
            float_value = float(value)
        except ValueError:
            return {
                "valid": False,
                "value": value,
                "error": "Not a valid float",
            }
        
        min_val = options.get("min")
        max_val = options.get("max")
        
        if min_val is not None and float_value < min_val:
            return {
                "valid": False,
                "value": float_value,
                "error": f"Value less than minimum {min_val}",
            }
        
        if max_val is not None and float_value > max_val:
            return {
                "valid": False,
                "value": float_value,
                "error": f"Value greater than maximum {max_val}",
            }
        
        return {"valid": True, "value": float_value, "error": None}
    
    @staticmethod
    def _validate_bool(value: str, **options) -> Dict[str, Any]:
        """Validate boolean type."""
        bool_value = value.lower() in ("true", "1", "yes", "on")
        return {"valid": True, "value": bool_value, "error": None}
    
    @staticmethod
    def _validate_url(value: str, **options) -> Dict[str, Any]:
        """Validate URL type."""
        try:
            parsed = urlparse(value)
            
            if not parsed.scheme:
                return {
                    "valid": False,
                    "value": value,
                    "error": "URL missing scheme (http/https)",
                }
            
            if not parsed.netloc:
                return {
                    "valid": False,
                    "value": value,
                    "error": "URL missing netloc (domain)",
                }
            
            return {"valid": True, "value": value, "error": None}
        
        except Exception as e:
            return {
                "valid": False,
                "value": value,
                "error": f"Invalid URL: {e}",
            }
    
    @staticmethod
    def _validate_port(value: str, **options) -> Dict[str, Any]:
        """Validate port type."""
        try:
            port = int(value)
            
            if port < 1 or port > 65535:
                return {
                    "valid": False,
                    "value": port,
                    "error": "Port out of range (1-65535)",
                }
            
            return {"valid": True, "value": port, "error": None}
        
        except ValueError:
            return {
                "valid": False,
                "value": value,
                "error": "Not a valid port number",
            }
    
    @staticmethod
    def _validate_path(value: str, **options) -> Dict[str, Any]:
        """Validate path type."""
        try:
            path = Path(value)
            
            if options.get("must_exist"):
                if not path.exists():
                    return {
                        "valid": False,
                        "value": value,
                        "error": f"Path does not exist: {value}",
                    }
            
            if options.get("must_be_file"):
                if not path.is_file():
                    return {
                        "valid": False,
                        "value": value,
                        "error": f"Path is not a file: {value}",
                    }
            
            if options.get("must_be_dir"):
                if not path.is_dir():
                    return {
                        "valid": False,
                        "value": value,
                        "error": f"Path is not a directory: {value}",
                    }
            
            return {"valid": True, "value": str(path.expanduser()), "error": None}
        
        except Exception as e:
            return {
                "valid": False,
                "value": value,
                "error": f"Invalid path: {e}",
            }


def validate_secrets_environment() -> Dict[str, Any]:
    """
    Pre-flight check for secrets management environment.
    
    Returns:
        Dict with "valid", "errors", "warnings"
        
    Raises:
        SecretsError: If critical checks fail
    """
    validator = EnvironmentValidator()
    
    # Add schema for secrets-related variables
    validator.add_schema(
        "CORTEX_MASTER_KEY",
        var_type="string",
        required=True,
        min_length=32,
    )
    
    validator.add_schema(
        "CORTEX_SECRETS_PATH",
        var_type="path",
        required=False,
        default=os.path.expanduser("~/.cortex/secrets"),
    )
    
    validator.add_schema(
        "CORTEX_AUDIT_ENABLED",
        var_type="bool",
        required=False,
        default=True,
    )
    
    # Validate
    result = validator.validate_all()
    
    if result["errors"]:
        logger.error(f"Environment validation failed: {result['errors']}")
    
    if result["warnings"]:
        logger.warning(f"Environment warnings: {result['warnings']}")
    
    return result


__all__ = [
    "EnvironmentValidator",
    "validate_secrets_environment",
]
