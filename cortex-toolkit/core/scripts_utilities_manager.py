"""
Scripts/Utilities Manager for CORTEX Toolkit.

Provides:
- Audit logging integration for scripts/utilities execution
- Usage intelligence and pattern analysis
- Cleanup recommendations
- Category-based organization
- CLI wrapper auto-generation

Part of Phase P05: Scripts/Utilities Toolkit Consolidation.
"""

import ast
import hashlib
import json
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Import audit logger using dynamic path resolution
try:
    # Add project root to path
    project_root = Path(__file__).resolve()
    for parent in [project_root.parent] + list(project_root.parents):
        if (parent / "cortex.config.json").exists():
            sys.path.insert(0, str(parent))
            break
    
    from cortex_toolkit.core.audit_logger import AuditLogger, ExecutionEvent
except ImportError:
    # Fallback: direct import from same directory
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "audit_logger",
        Path(__file__).parent / "audit_logger.py"
    )
    if spec and spec.loader:
        audit_logger_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(audit_logger_module)
        AuditLogger = audit_logger_module.AuditLogger
        ExecutionEvent = audit_logger_module.ExecutionEvent
    else:
        raise ImportError("Cannot import AuditLogger - audit_logger.py not found")


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class UtilityMetadata:
    """Metadata for a utility script."""
    
    name: str
    file_path: str
    category: str
    description: str
    capabilities: List[str]
    dependencies: List[str]
    usage_count: int = 0
    last_used: Optional[str] = None
    avg_duration_ms: float = 0.0
    success_rate: float = 100.0


@dataclass
class ExecutionStats:
    """Execution statistics for a utility."""
    
    total_executions: int
    successful_executions: int
    failed_executions: int
    total_duration_ms: int
    avg_duration_ms: float
    last_execution: Optional[str]
    success_rate: float


# =============================================================================
# Scripts/Utilities Manager
# =============================================================================

class ScriptsUtilitiesManager:
    """
    Manages scripts/utilities with audit logging, intelligence, and organization.
    
    Features:
    - Auto-discovery of utilities in scripts/utilities/
    - Category classification (analysis, database, migration, etc.)
    - Audit logging for all executions
    - Usage intelligence (patterns, recommendations)
    - Cleanup suggestions (archive/delete)
    - CLI wrapper auto-generation
    """
    
    def __init__(
        self,
        scripts_dir: str = "scripts/utilities",
        toolkit_dir: str = "cortex-toolkit/scripts-utilities",
        audit_log_path: Optional[str] = None,
    ):
        """
        Initialize the Scripts/Utilities Manager.
        
        Args:
            scripts_dir: Path to scripts/utilities directory
            toolkit_dir: Path to cortex-toolkit/scripts-utilities
            audit_log_path: Path to audit log (default: cortex-toolkit/logs/utilities-audit.jsonl)
        """
        self.scripts_dir = Path(scripts_dir)
        self.toolkit_dir = Path(toolkit_dir)
        self.audit_log_path = Path(audit_log_path or "cortex-toolkit/logs/utilities-audit.jsonl")
        
        # Initialize audit logger
        self.audit_logger = AuditLogger(str(self.audit_log_path))
        
        # Create toolkit directory structure
        self.toolkit_dir.mkdir(parents=True, exist_ok=True)
        self.audit_log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Category definitions
        self.categories = {
            "analysis": ["analyze", "profile", "benchmark"],
            "database": ["migrate", "schema", "validate_db"],
            "migration": ["migrate_", "migration"],
            "cleanup": ["cleanup", "deletion", "phase"],
            "validation": ["validate_phase", "validate_"],
            "dashboards": ["dashboard", "launch_"],
        }
    
    # =========================================================================
    # Discovery & Classification
    # =========================================================================
    
    def discover_utilities(self) -> List[UtilityMetadata]:
        """
        Discover all utilities in scripts/utilities directory.
        
        Returns:
            List of UtilityMetadata for discovered utilities
        """
        utilities = []
        
        if not self.scripts_dir.exists():
            return utilities
        
        for file_path in self.scripts_dir.glob("*.py"):
            metadata = self._extract_metadata(file_path)
            if metadata:
                utilities.append(metadata)
        
        return utilities
    
    def _extract_metadata(self, file_path: Path) -> Optional[UtilityMetadata]:
        """
        Extract metadata from a utility script.
        
        Args:
            file_path: Path to utility script
            
        Returns:
            UtilityMetadata or None if extraction fails
        """
        try:
            # Read file content
            content = file_path.read_text(encoding="utf-8")
            
            # Parse AST
            tree = ast.parse(content)
            
            # Extract docstring
            description = ast.get_docstring(tree) or "No description available"
            
            # Extract imports (dependencies)
            dependencies = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        dependencies.append(alias.name.split(".")[0])
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        dependencies.append(node.module.split(".")[0])
            
            # Classify category
            category = self._classify_category(file_path.name)
            
            # Extract capabilities (functions)
            capabilities = []
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    if not node.name.startswith("_"):  # Public functions only
                        capabilities.append(node.name)
            
            # Get execution stats
            stats = self._get_execution_stats(file_path.name)
            
            return UtilityMetadata(
                name=file_path.stem,
                file_path=str(file_path),
                category=category,
                description=description.split("\n")[0][:100],  # First line, truncated
                capabilities=capabilities[:5],  # Top 5 functions
                dependencies=list(set(dependencies))[:10],  # Unique, top 10
                usage_count=stats.total_executions if stats else 0,
                last_used=stats.last_execution if stats else None,
                avg_duration_ms=stats.avg_duration_ms if stats else 0.0,
                success_rate=stats.success_rate if stats else 100.0,
            )
        
        except Exception as e:
            print(f"⚠️  Failed to extract metadata from {file_path.name}: {e}")
            return None
    
    def _classify_category(self, filename: str) -> str:
        """
        Classify utility category based on filename patterns.
        
        Args:
            filename: Utility filename
            
        Returns:
            Category name (analysis, database, migration, etc.)
        """
        filename_lower = filename.lower()
        
        for category, patterns in self.categories.items():
            if any(pattern in filename_lower for pattern in patterns):
                return category
        
        return "general"
    
    # =========================================================================
    # Execution & Audit Logging
    # =========================================================================
    
    def execute_utility(
        self,
        utility_name: str,
        args: Optional[List[str]] = None,
        checkpoint_id: Optional[str] = None,
    ) -> Tuple[int, str, str]:
        """
        Execute a utility with audit logging.
        
        Args:
            utility_name: Name of utility to execute
            args: Command-line arguments
            checkpoint_id: Optional checkpoint ID for tracking
            
        Returns:
            Tuple of (exit_code, stdout, stderr)
        """
        args = args or []
        
        # Find utility file
        utility_path = self.scripts_dir / f"{utility_name}.py"
        if not utility_path.exists():
            return (1, "", f"Utility not found: {utility_name}")
        
        # Build command
        cmd = ["python3", str(utility_path)] + args
        
        # Execute with timing
        start_time = time.time()
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
            )
            duration_ms = int((time.time() - start_time) * 1000)
            
            # Log execution event
            event = ExecutionEvent(
                tool=utility_name,
                args=args,
                status="success" if result.returncode == 0 else "failed",
                exit_code=result.returncode,
                duration_ms=duration_ms,
                checkpoint_id=checkpoint_id,
                error=result.stderr if result.returncode != 0 else None,
            )
            self.audit_logger.log_execution(event)
            
            return (result.returncode, result.stdout, result.stderr)
        
        except subprocess.TimeoutExpired:
            duration_ms = int((time.time() - start_time) * 1000)
            event = ExecutionEvent(
                tool=utility_name,
                args=args,
                status="timeout",
                exit_code=-1,
                duration_ms=duration_ms,
                error="Execution timed out after 5 minutes",
            )
            self.audit_logger.log_execution(event)
            return (-1, "", "Execution timed out")
        
        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            event = ExecutionEvent(
                tool=utility_name,
                args=args,
                status="error",
                exit_code=-1,
                duration_ms=duration_ms,
                error=str(e),
            )
            self.audit_logger.log_execution(event)
            return (-1, "", str(e))
    
    def _get_execution_stats(self, utility_name: str) -> Optional[ExecutionStats]:
        """
        Get execution statistics from audit log.
        
        Args:
            utility_name: Name of utility
            
        Returns:
            ExecutionStats or None if no executions logged
        """
        if not self.audit_log_path.exists():
            return None
        
        try:
            total = 0
            successful = 0
            failed = 0
            total_duration = 0
            last_execution = None
            
            with open(self.audit_log_path, "r") as f:
                for line in f:
                    log_entry = json.loads(line)
                    if log_entry.get("event_type") == "execution" and log_entry.get("tool") == utility_name:
                        total += 1
                        if log_entry.get("status") == "success":
                            successful += 1
                        else:
                            failed += 1
                        total_duration += log_entry.get("duration_ms", 0)
                        last_execution = log_entry.get("timestamp")
            
            if total == 0:
                return None
            
            return ExecutionStats(
                total_executions=total,
                successful_executions=successful,
                failed_executions=failed,
                total_duration_ms=total_duration,
                avg_duration_ms=total_duration / total,
                last_execution=last_execution,
                success_rate=(successful / total) * 100,
            )
        
        except Exception:
            return None
    
    # =========================================================================
    # Usage Intelligence
    # =========================================================================
    
    def get_usage_patterns(self) -> Dict[str, Any]:
        """
        Analyze usage patterns across all utilities.
        
        Returns:
            Dictionary with usage insights
        """
        utilities = self.discover_utilities()
        
        # Group by category
        by_category = {}
        for util in utilities:
            if util.category not in by_category:
                by_category[util.category] = []
            by_category[util.category].append(util)
        
        # Find unused utilities
        unused = [u for u in utilities if u.usage_count == 0]
        
        # Find most used
        most_used = sorted(utilities, key=lambda u: u.usage_count, reverse=True)[:5]
        
        # Find slowest
        slowest = sorted(utilities, key=lambda u: u.avg_duration_ms, reverse=True)[:5]
        
        return {
            "total_utilities": len(utilities),
            "by_category": {cat: len(utils) for cat, utils in by_category.items()},
            "unused_count": len(unused),
            "unused_utilities": [u.name for u in unused],
            "most_used": [{"name": u.name, "count": u.usage_count} for u in most_used],
            "slowest": [{"name": u.name, "avg_ms": u.avg_duration_ms} for u in slowest],
        }
    
    def get_cleanup_recommendations(self) -> List[Dict[str, str]]:
        """
        Get cleanup recommendations for utilities.
        
        Returns:
            List of recommendations
        """
        utilities = self.discover_utilities()
        recommendations = []
        
        for util in utilities:
            # Recommend archiving unused utilities
            if util.usage_count == 0:
                recommendations.append({
                    "utility": util.name,
                    "action": "archive",
                    "reason": "Never used",
                    "priority": "low",
                })
            
            # Recommend review for low success rate
            elif util.success_rate < 50:
                recommendations.append({
                    "utility": util.name,
                    "action": "review",
                    "reason": f"Low success rate: {util.success_rate:.1f}%",
                    "priority": "high",
                })
            
            # Recommend optimization for slow utilities
            elif util.avg_duration_ms > 60000:  # > 1 minute
                recommendations.append({
                    "utility": util.name,
                    "action": "optimize",
                    "reason": f"Slow execution: {util.avg_duration_ms/1000:.1f}s avg",
                    "priority": "medium",
                })
        
        return recommendations


# =============================================================================
# CLI Entry Point
# =============================================================================

def main():
    """CLI entry point for testing."""
    manager = ScriptsUtilitiesManager()
    
    print("🔍 Discovering utilities...")
    utilities = manager.discover_utilities()
    print(f"✅ Found {len(utilities)} utilities\n")
    
    print("📊 Usage patterns:")
    patterns = manager.get_usage_patterns()
    print(json.dumps(patterns, indent=2))
    
    print("\n🧹 Cleanup recommendations:")
    recommendations = manager.get_cleanup_recommendations()
    for rec in recommendations:
        print(f"  - {rec['utility']}: {rec['action']} ({rec['reason']})")


if __name__ == "__main__":
    main()
