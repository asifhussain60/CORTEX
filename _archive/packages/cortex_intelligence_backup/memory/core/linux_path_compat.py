"""Linux-specific path compatibility handler with container and CI/CD support.

This module provides comprehensive Linux path handling including relative paths,
container environment support, CI/CD integration, and POSIX compliance validation.

Features:
- Relative to absolute path conversion
- Container path detection and parsing
- CI/CD environment variable expansion
- Linux reserved names detection
- Container cgroup path detection
- Symlink resolution in containers
- Path normalization for Linux
- Environment detection (Docker, GitHub Actions, GitLab CI, Jenkins)
- Linux special file detection
- Comprehensive path validation

Thread-Safe: All methods use appropriate locking for concurrent access.
"""

import os
import re
import threading
from pathlib import Path
from typing import Optional, Dict, List, Set
from threading import RLock


class LinuxPathCompatibility:
    """Linux-specific path compatibility handler with 12 major features.
    
    Provides comprehensive handling of Linux paths including support for:
    - Relative and absolute path conversion
    - Container environment detection and path handling
    - CI/CD environment variable expansion
    - Linux reserved system names
    - Container special paths (cgroup, proc, sys)
    - Symlink resolution in containerized environments
    - POSIX path compliance
    """

    # Linux reserved system directory names
    LINUX_RESERVED_DIRS: Set[str] = {
        "dev", "proc", "sys", "boot", "root", "lost+found",
        "mnt", "media", "run", "srv"
    }

    # Linux special device files
    LINUX_SPECIAL_FILES: Set[str] = {
        "/dev/null", "/dev/zero", "/dev/random", "/dev/urandom",
        "/dev/stdin", "/dev/stdout", "/dev/stderr"
    }

    # CI/CD environment variable patterns
    CI_VARIABLES: Dict[str, List[str]] = {
        "github_actions": ["GITHUB_WORKSPACE", "GITHUB_ACTION", "GITHUB_ACTIONS"],
        "gitlab_ci": ["CI_PROJECT_DIR", "GITLAB_CI", "CI_COMMIT_SHA"],
        "jenkins": ["JENKINS_HOME", "WORKSPACE", "BUILD_NUMBER"],
        "circleci": ["CIRCLE_WORKING_DIRECTORY", "CIRCLECI"],
        "travis": ["TRAVIS", "TRAVIS_BUILD_DIR"],
    }

    def __init__(self) -> None:
        """Initialize LinuxPathCompatibility handler."""
        self._lock = RLock()
        self._symlink_cache: Dict[str, Optional[str]] = {}
        self._is_container: Optional[bool] = None
        self._ci_environment: Optional[str] = None

    # ==================== Relative Path Handling ====================

    def relative_to_absolute(self, path: str) -> str:
        """Convert relative path to absolute path.
        
        Args:
            path: Relative path to convert (e.g., "./config/settings.ini")

        Returns:
            Absolute path (e.g., "/home/user/project/config/settings.ini")
        """
        with self._lock:
            if os.path.isabs(path):
                return os.path.abspath(path)
            
            # Get current working directory
            cwd = os.getcwd()
            absolute = os.path.join(cwd, path)
            
            # Normalize to remove .. and .
            return os.path.normpath(absolute)

    def is_relative_path(self, path: str) -> bool:
        """Check if path is relative.
        
        Args:
            path: Path to check

        Returns:
            True if path is relative, False otherwise
        """
        with self._lock:
            return not os.path.isabs(path)

    def is_absolute_path(self, path: str) -> bool:
        """Check if path is absolute.
        
        Args:
            path: Path to check

        Returns:
            True if path is absolute, False otherwise
        """
        with self._lock:
            return os.path.isabs(path)

    # ==================== Container Path Handling ====================

    def is_container_path(self, path: str) -> bool:
        """Detect if path is a container-specific path.
        
        Container paths typically include /app, /workspace, /mnt volumes.
        
        Args:
            path: Path to check

        Returns:
            True if path appears to be a container path
        """
        with self._lock:
            container_indicators = [
                "/app", "/workspace", "/mnt", "/home/runner",
                "/builds", "/var/run/docker", "/.dockerenv"
            ]
            
            for indicator in container_indicators:
                if path.startswith(indicator):
                    return True
            
            return False

    def parse_container_mount(self, mount_spec: str) -> Optional[Dict[str, str]]:
        """Parse container volume mount specification.
        
        Args:
            mount_spec: Mount specification (e.g., "/host/path:/container/path")

        Returns:
            Dict with 'host_path' and 'container_path', or None if invalid
        """
        with self._lock:
            if ":" not in mount_spec:
                return None
            
            parts = mount_spec.split(":")
            if len(parts) < 2:
                return None
            
            return {
                "host_path": parts[0],
                "container_path": parts[1]
            }

    def is_cgroup_path(self, path: str) -> bool:
        """Check if path is a cgroup path.
        
        Cgroup paths are container control group paths used by Linux containers.
        
        Args:
            path: Path to check

        Returns:
            True if path is a cgroup path
        """
        with self._lock:
            cgroup_patterns = [
                "/sys/fs/cgroup",
                "/proc/*/cgroup",
                "/sys/fs/cgroup/",
            ]
            
            for pattern in cgroup_patterns:
                if path.startswith(pattern.replace("*", "")):
                    return True
            
            return False

    # ==================== CI/CD Environment ====================

    def expand_ci_variables(self, path: str) -> str:
        """Expand CI/CD environment variables in path.
        
        Replaces $VAR_NAME with environment variable values.
        Supports GitHub Actions, GitLab CI, Jenkins, etc.
        
        Args:
            path: Path with variables (e.g., "$CI_PROJECT_DIR/src")

        Returns:
            Path with expanded variables
        """
        with self._lock:
            result = path
            
            # Find all $VARIABLE patterns
            pattern = r'\$([A-Z_][A-Z0-9_]*)'
            matches = re.findall(pattern, result)
            
            for var_name in matches:
                var_value = os.environ.get(var_name, "")
                result = result.replace(f"${var_name}", var_value)
            
            return result

    def is_github_actions_environment(self) -> bool:
        """Check if running in GitHub Actions environment.
        
        Returns:
            True if running in GitHub Actions
        """
        with self._lock:
            return "GITHUB_ACTIONS" in os.environ

    def is_gitlab_ci_environment(self) -> bool:
        """Check if running in GitLab CI environment.
        
        Returns:
            True if running in GitLab CI
        """
        with self._lock:
            return "GITLAB_CI" in os.environ

    def is_jenkins_environment(self) -> bool:
        """Check if running in Jenkins environment.
        
        Returns:
            True if running in Jenkins
        """
        with self._lock:
            return "JENKINS_HOME" in os.environ

    def get_ci_environment(self) -> Optional[str]:
        """Detect which CI/CD environment is active.
        
        Returns:
            String identifying CI environment, or None if not in CI
        """
        with self._lock:
            if self._ci_environment is not None:
                return self._ci_environment
            
            if self.is_github_actions_environment():
                self._ci_environment = "github_actions"
            elif self.is_gitlab_ci_environment():
                self._ci_environment = "gitlab_ci"
            elif self.is_jenkins_environment():
                self._ci_environment = "jenkins"
            else:
                # Check other CI systems
                if "CIRCLECI" in os.environ:
                    self._ci_environment = "circleci"
                elif "TRAVIS" in os.environ:
                    self._ci_environment = "travis"
                else:
                    self._ci_environment = None
            
            return self._ci_environment

    # ==================== Path Validation ====================

    def is_linux_reserved_name(self, name: str) -> bool:
        """Check if name is a Linux reserved system directory name.
        
        Args:
            name: Directory name to check

        Returns:
            True if name is reserved
        """
        with self._lock:
            return name.lower() in self.LINUX_RESERVED_DIRS

    def is_linux_special_file(self, path: str) -> bool:
        """Check if path is a Linux special file.
        
        Special files include /dev/null, /dev/random, etc.
        
        Args:
            path: Path to check

        Returns:
            True if path is a special file
        """
        with self._lock:
            return path in self.LINUX_SPECIAL_FILES or path.startswith("/dev/")

    def validate_linux_path(self, path: str) -> bool:
        """Validate Linux path for correctness.
        
        Checks:
        - Path uses forward slashes (POSIX)
        - No null bytes
        - No backslashes
        - Component length <= 255
        
        Args:
            path: Path to validate

        Returns:
            True if path is valid
        """
        with self._lock:
            if not path:
                return False
            
            # Check for null bytes
            if '\x00' in path:
                return False
            
            # Check for backslashes (Windows paths not valid in Linux)
            if '\\' in path:
                return False
            
            # Check component length
            for component in path.split('/'):
                if component and len(component) > 255:
                    return False
            
            return True

    # ==================== Symlink Handling ====================

    def resolve_symlink_in_container(self, path: str) -> Optional[str]:
        """Resolve symlink in container environment.
        
        Handles symlinks that may point outside container boundaries.
        
        Args:
            path: Symlink path to resolve

        Returns:
            Resolved path, or None if symlink cannot be resolved
        """
        with self._lock:
            if path in self._symlink_cache:
                return self._symlink_cache[path]
            
            try:
                if os.path.islink(path):
                    result = os.path.realpath(path)
                    self._symlink_cache[path] = result
                    return result
                else:
                    return path
            except (OSError, RuntimeError):
                self._symlink_cache[path] = None
                return None

    # ==================== Path Normalization ====================

    def normalize_linux_path(self, path: str) -> str:
        """Normalize Linux path.
        
        Removes redundant slashes, resolves . and .., handles backslashes.
        
        Args:
            path: Path to normalize

        Returns:
            Normalized path
        """
        with self._lock:
            if not path:
                return path
            
            # Convert backslashes to forward slashes
            normalized = path.replace('\\', '/')
            
            # Use os.path.normpath but ensure it stays POSIX-compliant
            normalized = os.path.normpath(normalized)
            
            # Ensure forward slashes on result
            normalized = normalized.replace('\\', '/')
            
            return normalized

    def has_mixed_separators(self, path: str) -> bool:
        """Check if path has mixed path separators.
        
        Linux paths should only use forward slashes.
        
        Args:
            path: Path to check

        Returns:
            True if path has both / and \
        """
        with self._lock:
            has_forward = "/" in path
            has_backslash = "\\" in path
            return has_forward and has_backslash

    # ==================== Container Detection ====================

    def is_running_in_container(self) -> bool:
        """Detect if running inside a container.
        
        Checks for Docker/container indicators like /.dockerenv file
        or cgroup entries.
        
        Returns:
            True if running in container
        """
        with self._lock:
            if self._is_container is not None:
                return self._is_container
            
            # Check for .dockerenv file
            if os.path.exists("/.dockerenv"):
                self._is_container = True
                return True
            
            # Check cgroup file for container indicators
            try:
                with open("/proc/self/cgroup", "r") as f:
                    content = f.read()
                    if "docker" in content or "container" in content or "kubepods" in content:
                        self._is_container = True
                        return True
            except (OSError, IOError):
                pass
            
            self._is_container = False
            return False

    # ==================== Path Composition ====================

    def join_paths(self, *path_components: str) -> str:
        """Join path components into a single POSIX path.
        
        Args:
            *path_components: Path components to join

        Returns:
            Joined POSIX path
        """
        with self._lock:
            if not path_components:
                return ""
            
            # Join using forward slash
            result = "/".join(component.strip("/") for component in path_components)
            
            # Ensure it starts with / for absolute paths
            if path_components and path_components[0].startswith("/"):
                result = "/" + result
            
            return result

    def get_path_depth(self, path: str) -> int:
        """Calculate path depth (number of components).
        
        Args:
            path: Path to analyze

        Returns:
            Number of path components (excluding root)
        """
        with self._lock:
            if not path or path == "/":
                return 0
            
            # Remove leading/trailing slashes
            cleaned = path.strip("/")
            
            if not cleaned:
                return 0
            
            return len(cleaned.split("/"))


if __name__ == "__main__":
    # Example usage
    compat = LinuxPathCompatibility()
    
    # Test relative path handling
    print(f"Current dir: {os.getcwd()}")
    print(f"Is relative './config': {compat.is_relative_path('./config')}")
    print(f"Is absolute '/etc/config': {compat.is_absolute_path('/etc/config')}")
    
    # Test container detection
    print(f"Is container path '/app': {compat.is_container_path('/app')}")
    
    # Test CI environment
    print(f"CI environment: {compat.get_ci_environment()}")
    
    # Test path validation
    print(f"Valid path '/etc/nginx': {compat.validate_linux_path('/etc/nginx')}")
