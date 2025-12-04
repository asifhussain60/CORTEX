"""
Environment diagnostics system for CORTEX
Checks Python environment, git status, system resources, installed packages

Part of Phase 4: Alignment Orchestrator
"""

import importlib
import platform
import shutil
import socket
import subprocess
import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import List, Dict, Any, Optional

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False


class DiagnosticStatus(Enum):
    """Status levels for diagnostic results"""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    INFO = "info"


class DiagnosticCategory(Enum):
    """Categories of diagnostic checks"""
    PYTHON = "python"
    GIT = "git"
    SYSTEM = "system"
    NETWORK = "network"


@dataclass
class DiagnosticResult:
    """Result of a diagnostic check"""
    category: DiagnosticCategory
    status: DiagnosticStatus
    message: str
    details: Dict[str, Any]


class EnvironmentDiagnostics:
    """
    Diagnostic system for CORTEX environment
    
    Checks:
    - Python version and packages
    - Git repository status
    - Disk space and memory
    - System resources
    - Network connectivity
    """
    
    REQUIRED_PYTHON_VERSION = (3, 8)
    REQUIRED_PACKAGES = [
        "yaml",
        "sqlite3",
        "pydantic",
        "pytest"
    ]
    
    DISK_WARNING_THRESHOLD = 85  # Percent
    DISK_CRITICAL_THRESHOLD = 95
    MEMORY_WARNING_THRESHOLD = 85
    
    def __init__(self, root_path: Path):
        """
        Initialize diagnostics system
        
        Args:
            root_path: Path to CORTEX root directory
        """
        self.root_path = Path(root_path)
    
    def check_python_version(self) -> DiagnosticResult:
        """
        Check Python version meets minimum requirements
        
        Returns:
            DiagnosticResult with Python version info
        """
        version = sys.version_info
        version_str = f"{version.major}.{version.minor}.{version.micro}"
        
        if version[:2] >= self.REQUIRED_PYTHON_VERSION:
            status = DiagnosticStatus.HEALTHY
            message = f"Python {version_str} meets requirements (>= {self.REQUIRED_PYTHON_VERSION[0]}.{self.REQUIRED_PYTHON_VERSION[1]})"
        else:
            status = DiagnosticStatus.CRITICAL
            message = f"Python {version_str} below minimum requirement {self.REQUIRED_PYTHON_VERSION[0]}.{self.REQUIRED_PYTHON_VERSION[1]}"
        
        return DiagnosticResult(
            category=DiagnosticCategory.PYTHON,
            status=status,
            message=message,
            details={
                "version": version_str,
                "major": version.major,
                "minor": version.minor,
                "platform": platform.platform()
            }
        )
    
    def check_git_status(self) -> DiagnosticResult:
        """
        Check git repository status
        
        Returns:
            DiagnosticResult with git status info
        """
        try:
            # Check for uncommitted changes
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.root_path,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode != 0:
                return DiagnosticResult(
                    category=DiagnosticCategory.GIT,
                    status=DiagnosticStatus.WARNING,
                    message="Not a git repository or git not available",
                    details={}
                )
            
            changes = result.stdout.strip()
            
            if not changes:
                status = DiagnosticStatus.HEALTHY
                message = "Working tree clean, no uncommitted changes"
            else:
                status = DiagnosticStatus.INFO
                lines = changes.split('\n')
                message = f"Found {len(lines)} uncommitted changes"
            
            # Get current branch
            branch_result = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=self.root_path,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            branch = branch_result.stdout.strip() if branch_result.returncode == 0 else "unknown"
            
            return DiagnosticResult(
                category=DiagnosticCategory.GIT,
                status=status,
                message=message,
                details={
                    "branch": branch,
                    "changes": len(changes.split('\n')) if changes else 0
                }
            )
        
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            return DiagnosticResult(
                category=DiagnosticCategory.GIT,
                status=DiagnosticStatus.WARNING,
                message=f"Git check failed: {str(e)}",
                details={}
            )
    
    def check_disk_space(self) -> DiagnosticResult:
        """
        Check available disk space
        
        Returns:
            DiagnosticResult with disk space info
        """
        try:
            usage = shutil.disk_usage(self.root_path)
            
            percent_used = (usage.used / usage.total) * 100
            available_gb = usage.free / (1024**3)
            
            if percent_used >= self.DISK_CRITICAL_THRESHOLD:
                status = DiagnosticStatus.CRITICAL
                message = f"Disk critically low: {available_gb:.1f} GB available ({percent_used:.1f}% used)"
            elif percent_used >= self.DISK_WARNING_THRESHOLD:
                status = DiagnosticStatus.WARNING
                message = f"Disk space low: {available_gb:.1f} GB available ({percent_used:.1f}% used)"
            else:
                status = DiagnosticStatus.HEALTHY
                message = f"Sufficient disk space: {available_gb:.1f} GB available ({percent_used:.1f}% used)"
            
            return DiagnosticResult(
                category=DiagnosticCategory.SYSTEM,
                status=status,
                message=message,
                details={
                    "available_gb": round(available_gb, 2),
                    "total_gb": round(usage.total / (1024**3), 2),
                    "percent_used": round(percent_used, 1)
                }
            )
        
        except Exception as e:
            return DiagnosticResult(
                category=DiagnosticCategory.SYSTEM,
                status=DiagnosticStatus.WARNING,
                message=f"Could not check disk space: {str(e)}",
                details={}
            )
    
    def check_memory_usage(self) -> DiagnosticResult:
        """
        Check system memory usage
        
        Returns:
            DiagnosticResult with memory info
        """
        if not PSUTIL_AVAILABLE:
            return DiagnosticResult(
                category=DiagnosticCategory.SYSTEM,
                status=DiagnosticStatus.INFO,
                message="psutil not available, cannot check memory",
                details={}
            )
        
        try:
            mem = psutil.virtual_memory()
            
            available_gb = mem.available / (1024**3)
            percent_used = mem.percent
            
            if percent_used >= self.MEMORY_WARNING_THRESHOLD:
                status = DiagnosticStatus.WARNING
                message = f"Memory usage high: {available_gb:.1f} GB available ({percent_used:.1f}% used)"
            else:
                status = DiagnosticStatus.HEALTHY
                message = f"Memory usage normal: {available_gb:.1f} GB available ({percent_used:.1f}% used)"
            
            return DiagnosticResult(
                category=DiagnosticCategory.SYSTEM,
                status=status,
                message=message,
                details={
                    "available_gb": round(available_gb, 2),
                    "total_gb": round(mem.total / (1024**3), 2),
                    "percent_used": round(percent_used, 1)
                }
            )
        
        except Exception as e:
            return DiagnosticResult(
                category=DiagnosticCategory.SYSTEM,
                status=DiagnosticStatus.WARNING,
                message=f"Could not check memory: {str(e)}",
                details={}
            )
    
    def check_installed_packages(self) -> DiagnosticResult:
        """
        Check installed Python packages
        
        Returns:
            DiagnosticResult with package list
        """
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "list", "--format=json"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                import json
                packages = json.loads(result.stdout)
                
                return DiagnosticResult(
                    category=DiagnosticCategory.PYTHON,
                    status=DiagnosticStatus.HEALTHY,
                    message=f"Found {len(packages)} installed packages",
                    details={"packages": packages}
                )
            else:
                return DiagnosticResult(
                    category=DiagnosticCategory.PYTHON,
                    status=DiagnosticStatus.WARNING,
                    message="Could not list installed packages",
                    details={"packages": []}
                )
        
        except Exception as e:
            return DiagnosticResult(
                category=DiagnosticCategory.PYTHON,
                status=DiagnosticStatus.WARNING,
                message=f"Package check failed: {str(e)}",
                details={"packages": []}
            )
    
    def check_required_packages(self) -> DiagnosticResult:
        """
        Check required Python packages are installed
        
        Returns:
            DiagnosticResult with required packages status
        """
        missing = []
        present = []
        
        for package in self.REQUIRED_PACKAGES:
            try:
                importlib.import_module(package)
                present.append(package)
            except ImportError:
                missing.append(package)
        
        if not missing:
            status = DiagnosticStatus.HEALTHY
            message = f"All {len(present)} required packages installed"
        else:
            status = DiagnosticStatus.CRITICAL
            message = f"Missing {len(missing)} required packages: {', '.join(missing)}"
        
        return DiagnosticResult(
            category=DiagnosticCategory.PYTHON,
            status=status,
            message=message,
            details={
                "present": present,
                "missing": missing
            }
        )
    
    def check_cortex_processes(self) -> DiagnosticResult:
        """
        Check for running CORTEX processes
        
        Returns:
            DiagnosticResult with process info
        """
        if not PSUTIL_AVAILABLE:
            return DiagnosticResult(
                category=DiagnosticCategory.SYSTEM,
                status=DiagnosticStatus.INFO,
                message="psutil not available, cannot check processes",
                details={}
            )
        
        try:
            cortex_procs = []
            for proc in psutil.process_iter(['name', 'cmdline']):
                try:
                    cmdline = proc.info.get('cmdline', [])
                    if cmdline and any('cortex' in str(arg).lower() for arg in cmdline):
                        cortex_procs.append({
                            "name": proc.info['name'],
                            "pid": proc.pid
                        })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            if cortex_procs:
                message = f"Found {len(cortex_procs)} CORTEX process(es) running"
                status = DiagnosticStatus.INFO
            else:
                message = "No CORTEX processes currently running"
                status = DiagnosticStatus.INFO
            
            return DiagnosticResult(
                category=DiagnosticCategory.SYSTEM,
                status=status,
                message=message,
                details={"processes": cortex_procs}
            )
        
        except Exception as e:
            return DiagnosticResult(
                category=DiagnosticCategory.SYSTEM,
                status=DiagnosticStatus.WARNING,
                message=f"Process check failed: {str(e)}",
                details={}
            )
    
    def check_port_availability(self, port: int = 8080) -> DiagnosticResult:
        """
        Check if a port is available
        
        Args:
            port: Port number to check
            
        Returns:
            DiagnosticResult with port availability
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('localhost', port))
            sock.close()
            
            if result == 0:
                # Port is in use
                status = DiagnosticStatus.WARNING
                message = f"Port {port} is already in use"
            else:
                # Port is available
                status = DiagnosticStatus.HEALTHY
                message = f"Port {port} is available"
            
            return DiagnosticResult(
                category=DiagnosticCategory.NETWORK,
                status=status,
                message=message,
                details={"port": port, "available": result != 0}
            )
        
        except Exception as e:
            return DiagnosticResult(
                category=DiagnosticCategory.NETWORK,
                status=DiagnosticStatus.WARNING,
                message=f"Port check failed: {str(e)}",
                details={"port": port}
            )
    
    def run_all(self) -> List[DiagnosticResult]:
        """
        Run all diagnostic checks
        
        Returns:
            List of all DiagnosticResults
        """
        results = [
            self.check_python_version(),
            self.check_required_packages(),
            self.check_git_status(),
            self.check_disk_space(),
            self.check_memory_usage(),
            self.check_installed_packages(),
            self.check_cortex_processes()
        ]
        
        return results
    
    def generate_report(self, results: List[DiagnosticResult]) -> str:
        """
        Generate human-readable diagnostic report
        
        Args:
            results: List of DiagnosticResults
            
        Returns:
            Formatted report string
        """
        lines = []
        lines.append("=" * 70)
        lines.append("CORTEX ENVIRONMENT DIAGNOSTICS REPORT")
        lines.append("=" * 70)
        lines.append("")
        
        # Group by category
        by_category = {}
        for result in results:
            category = result.category.value
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(result)
        
        # Report each category
        for category, cat_results in by_category.items():
            lines.append(f"\n{category.upper()}")
            lines.append("-" * 70)
            
            for result in cat_results:
                status_icon = {
                    DiagnosticStatus.HEALTHY: "✅",
                    DiagnosticStatus.WARNING: "⚠️",
                    DiagnosticStatus.CRITICAL: "❌",
                    DiagnosticStatus.INFO: "ℹ️"
                }.get(result.status, "")
                
                lines.append(f"\n{status_icon} {result.message}")
                
                if result.details:
                    for key, value in result.details.items():
                        if not isinstance(value, (list, dict)):
                            lines.append(f"  {key}: {value}")
        
        lines.append("")
        lines.append("=" * 70)
        
        return "\n".join(lines)
