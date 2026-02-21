"""
Cleanup Auditor: WAVE-J (ENH-085) Completed Phase Cleanup Audit

Authority: WAVE-6-COMPREHENSIVE-CLEANUP-REFACTORING.yaml ENH-085
Purpose: Systematic audit + cleanup of completed phases and orphaned components
Dependencies: ENH-084 (phase validation capability)

AC_START: AC-WAVE-J-001
"""

import os
import yaml
import click
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any, Set, Optional
from dataclasses import dataclass, field
from collections import defaultdict
import subprocess
import ast


@dataclass
class FileArtifact:
    """Represents a file discovered during audit."""
    path: Path
    classification: str  # essential | stale | orphaned | deprecated
    last_modified: datetime
    last_commit_date: Optional[datetime]
    import_count: int
    phase_id: Optional[str]
    size_bytes: int
    recommendation: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for reporting."""
        return {
            "path": str(self.path),
            "classification": self.classification,
            "last_modified": self.last_modified.isoformat(),
            "last_commit_date": self.last_commit_date.isoformat() if self.last_commit_date else None,
            "import_count": self.import_count,
            "phase_id": self.phase_id,
            "size_kb": round(self.size_bytes / 1024, 2),
            "recommendation": self.recommendation,
        }


@dataclass
class AuditResult:
    """Results from cleanup audit."""
    total_files_scanned: int = 0
    completed_phases_found: int = 0
    essential_files: List[FileArtifact] = field(default_factory=list)
    stale_files: List[FileArtifact] = field(default_factory=list)
    orphaned_files: List[FileArtifact] = field(default_factory=list)
    deprecated_files: List[FileArtifact] = field(default_factory=list)
    cleanup_savings_kb: int = 0
    phases_to_migrate: List[str] = field(default_factory=list)
    
    def summary(self) -> Dict[str, Any]:
        """Generate summary statistics."""
        return {
            "total_scanned": self.total_files_scanned,
            "completed_phases": self.completed_phases_found,
            "classification": {
                "essential": len(self.essential_files),
                "stale": len(self.stale_files),
                "orphaned": len(self.orphaned_files),
                "deprecated": len(self.deprecated_files),
            },
            "cleanup_potential_mb": round(self.cleanup_savings_kb / 1024, 2),
            "phases_to_migrate": len(self.phases_to_migrate),
        }


class CleanupAuditor:
    """Performs systematic audit of completed phases and artifacts."""
    
    def __init__(self, workspace_root: Path) -> None:
        """Initialize auditor with workspace root."""
        self.workspace_root = workspace_root
        self.cortex_dir = workspace_root / "cortex"
        self.cortex_intelligence_dir = workspace_root / "cortex_intelligence"
        self.registry_dir = workspace_root / "cortex-registry" / "_cortex-master"
        self.active_phases_dir = self.registry_dir / "phases" / "active"
        self.completed_phases_dir = self.registry_dir / "phases" / "completed"
        
        # Import graph cache
        self._import_graph: Dict[str, Set[str]] = defaultdict(set)
        self._inbound_references: Dict[str, int] = defaultdict(int)
        
    def audit_completed_phases(self) -> List[str]:
        """Scan active phases folder for completed phases."""
        completed = []
        
        if not self.active_phases_dir.exists():
            return completed
        
        for yaml_file in self.active_phases_dir.glob("*.yaml"):
            try:
                with open(yaml_file) as f:
                    spec = yaml.safe_load(f)
                
                status = spec.get("status", "").lower()
                if status in ["complete", "completed", "done"]:
                    phase_id = spec.get("enhancement_id") or spec.get("phase_id") or yaml_file.stem
                    completed.append(phase_id)
            except Exception:
                # Skip invalid YAML files
                continue
        
        return completed
    
    def build_import_graph(self) -> None:
        """Build import graph for all Python files in cortex/."""
        click.echo("Building import graph...")
        
        for py_file in self.cortex_dir.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue
            
            try:
                with open(py_file) as f:
                    tree = ast.parse(f.read())
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            self._import_graph[str(py_file)].add(alias.name)
                            self._inbound_references[alias.name] += 1
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            self._import_graph[str(py_file)].add(node.module)
                            self._inbound_references[node.module] += 1
            except Exception:
                # Skip files with parse errors
                continue
    
    def get_file_last_commit(self, file_path: Path) -> Optional[datetime]:
        """Get last git commit date for file."""
        try:
            result = subprocess.run(
                ["git", "log", "-1", "--format=%at", "--", str(file_path)],
                cwd=self.workspace_root,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0 and result.stdout.strip():
                timestamp = int(result.stdout.strip())
                return datetime.fromtimestamp(timestamp)
        except Exception:
            pass
        
        return None
    
    def classify_file(self, file_path: Path, completed_phases: List[str]) -> FileArtifact:
        """Classify a file based on audit rules."""
        # Get file metadata
        stats = file_path.stat()
        last_modified = datetime.fromtimestamp(stats.st_mtime)
        last_commit = self.get_file_last_commit(file_path)
        size_bytes = stats.st_size
        
        # Check import count
        module_name = str(file_path.relative_to(self.workspace_root)).replace("/", ".").replace(".py", "")
        import_count = self._inbound_references.get(module_name, 0)
        
        # Attempt to extract phase ID from file
        phase_id = None
        for phase in completed_phases:
            if phase.lower() in str(file_path).lower():
                phase_id = phase
                break
        
        # Classification logic
        age_days = (datetime.now() - last_modified).days
        commit_age_days = (datetime.now() - last_commit).days if last_commit else 999
        
        # Rule 1: Essential (core infrastructure)
        if import_count >= 5 or "core" in str(file_path) or "orchestrators" in str(file_path):
            classification = "essential"
            recommendation = "Keep - core infrastructure"
        
        # Rule 2: Orphaned (0 imports + old)
        elif import_count == 0 and age_days > 180:
            classification = "orphaned"
            recommendation = "Archive to __cleanup-archive/"
        
        # Rule 3: Stale (completed phase not migrated)
        elif phase_id and phase_id in completed_phases:
            classification = "stale"
            recommendation = f"Migrate {phase_id} to completed/"
        
        # Rule 4: Deprecated (no recent commits)
        elif commit_age_days > 180 and import_count < 2:
            classification = "deprecated"
            recommendation = "Verify 0 imports then delete"
        
        else:
            classification = "essential"
            recommendation = "Keep - still in use"
        
        return FileArtifact(
            path=file_path,
            classification=classification,
            last_modified=last_modified,
            last_commit_date=last_commit,
            import_count=import_count,
            phase_id=phase_id,
            size_bytes=size_bytes,
            recommendation=recommendation,
        )
    
    def audit_workspace(self) -> AuditResult:
        """Perform comprehensive workspace audit."""
        result = AuditResult()
        
        # Step 1: Discover completed phases
        click.echo("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        click.echo("🔍 WAVE-J: Cleanup Audit")
        click.echo("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        click.echo()
        
        completed_phases = self.audit_completed_phases()
        result.completed_phases_found = len(completed_phases)
        result.phases_to_migrate = completed_phases
        
        click.echo(f"✅ Discovered {len(completed_phases)} completed phases")
        
        # Step 2: Build import graph
        self.build_import_graph()
        click.echo(f"✅ Built import graph ({len(self._import_graph)} files)")
        
        # Step 3: Scan cortex/ directory
        click.echo()
        click.echo("Scanning cortex/ directory...")
        
        for py_file in self.cortex_dir.rglob("*.py"):
            if "__pycache__" in str(py_file) or "__init__.py" == py_file.name:
                continue
            
            result.total_files_scanned += 1
            artifact = self.classify_file(py_file, completed_phases)
            
            # Add to appropriate list
            if artifact.classification == "essential":
                result.essential_files.append(artifact)
            elif artifact.classification == "stale":
                result.stale_files.append(artifact)
                result.cleanup_savings_kb += artifact.size_bytes // 1024
            elif artifact.classification == "orphaned":
                result.orphaned_files.append(artifact)
                result.cleanup_savings_kb += artifact.size_bytes // 1024
            elif artifact.classification == "deprecated":
                result.deprecated_files.append(artifact)
                result.cleanup_savings_kb += artifact.size_bytes // 1024
        
        # Step 4: Scan cortex_intelligence/ directory (if exists)
        if self.cortex_intelligence_dir.exists():
            click.echo("Scanning cortex_intelligence/ directory...")
            
            for py_file in self.cortex_intelligence_dir.rglob("*.py"):
                if "__pycache__" in str(py_file) or "__init__.py" == py_file.name:
                    continue
                
                result.total_files_scanned += 1
                artifact = self.classify_file(py_file, completed_phases)
                
                if artifact.classification == "essential":
                    result.essential_files.append(artifact)
                elif artifact.classification == "stale":
                    result.stale_files.append(artifact)
                    result.cleanup_savings_kb += artifact.size_bytes // 1024
                elif artifact.classification == "orphaned":
                    result.orphaned_files.append(artifact)
                    result.cleanup_savings_kb += artifact.size_bytes // 1024
                elif artifact.classification == "deprecated":
                    result.deprecated_files.append(artifact)
                    result.cleanup_savings_kb += artifact.size_bytes // 1024
        
        return result
    
    def generate_report(self, result: AuditResult, output_format: str = "text") -> str:
        """Generate audit report in specified format."""
        if output_format == "yaml":
            return self._generate_yaml_report(result)
        else:
            return self._generate_text_report(result)
    
    def _generate_text_report(self, result: AuditResult) -> str:
        """Generate human-readable text report."""
        lines = []
        
        lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        lines.append("📊 WAVE-J CLEANUP AUDIT REPORT")
        lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        lines.append("")
        
        # Summary
        summary = result.summary()
        lines.append("## Summary")
        lines.append("")
        lines.append(f"Total Files Scanned: {summary['total_scanned']}")
        lines.append(f"Completed Phases: {summary['completed_phases']}")
        lines.append("")
        
        lines.append("### Classification Breakdown")
        lines.append("")
        for category, count in summary['classification'].items():
            lines.append(f"  {category.capitalize()}: {count}")
        lines.append("")
        
        lines.append(f"Cleanup Potential: {summary['cleanup_potential_mb']:.2f} MB")
        lines.append(f"Phases to Migrate: {summary['phases_to_migrate']}")
        lines.append("")
        
        # Detailed listings
        if result.stale_files:
            lines.append("## 🟡 Stale Files (Completed Phases Not Migrated)")
            lines.append("")
            for artifact in result.stale_files[:10]:  # Top 10
                lines.append(f"  - {artifact.path.relative_to(self.workspace_root)}")
                lines.append(f"    Phase: {artifact.phase_id}")
                lines.append(f"    Recommendation: {artifact.recommendation}")
                lines.append("")
        
        if result.orphaned_files:
            lines.append("## 🔴 Orphaned Files (0 Imports + Old)")
            lines.append("")
            for artifact in result.orphaned_files[:10]:  # Top 10
                lines.append(f"  - {artifact.path.relative_to(self.workspace_root)}")
                lines.append(f"    Age: {(datetime.now() - artifact.last_modified).days} days")
                lines.append(f"    Recommendation: {artifact.recommendation}")
                lines.append("")
        
        if result.deprecated_files:
            lines.append("## ⚪ Deprecated Files (No Recent Commits)")
            lines.append("")
            for artifact in result.deprecated_files[:10]:  # Top 10
                lines.append(f"  - {artifact.path.relative_to(self.workspace_root)}")
                lines.append(f"    Last Commit: {artifact.last_commit_date.date() if artifact.last_commit_date else 'Unknown'}")
                lines.append(f"    Recommendation: {artifact.recommendation}")
                lines.append("")
        
        lines.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        lines.append("")
        lines.append("📋 Next Actions:")
        lines.append("")
        lines.append("1. Review stale files → Migrate to completed/")
        lines.append("2. Review orphaned files → Archive to __cleanup-archive/")
        lines.append("3. Review deprecated files → Verify 0 imports then delete")
        lines.append("4. Run cleanup script: cortex-cleanup-execute")
        lines.append("")
        
        return "\n".join(lines)
    
    def _generate_yaml_report(self, result: AuditResult) -> str:
        """Generate YAML report for programmatic processing."""
        report_data = {
            "audit_date": datetime.now().isoformat(),
            "summary": result.summary(),
            "stale_files": [a.to_dict() for a in result.stale_files],
            "orphaned_files": [a.to_dict() for a in result.orphaned_files],
            "deprecated_files": [a.to_dict() for a in result.deprecated_files],
            "phases_to_migrate": result.phases_to_migrate,
        }
        
        return yaml.dump(report_data, default_flow_style=False, sort_keys=False)


@click.group()
def cli() -> None:
    """WAVE-J: Cleanup Auditor CLI"""
    pass


@cli.command()
@click.option("--workspace", type=click.Path(exists=True), default=".", help="Workspace root directory")
@click.option("--format", type=click.Choice(["text", "yaml"]), default="text", help="Output format")
@click.option("--output", type=click.Path(), help="Save report to file (optional)")
def audit(workspace: str, format: str, output: Optional[str]) -> None:
    """
    Audit workspace for completed phases and orphaned components.
    
    Example:
        cortex-cleanup-audit --format yaml --output audit-report.yaml
    """
    workspace_path = Path(workspace).resolve()
    auditor = CleanupAuditor(workspace_path)
    
    # Perform audit
    result = auditor.audit_workspace()
    
    # Generate report
    report = auditor.generate_report(result, output_format=format)
    
    # Display or save
    if output:
        with open(output, "w") as f:
            f.write(report)
        click.echo(f"✅ Report saved to: {output}")
    else:
        click.echo(report)


@cli.command()
@click.option("--workspace", type=click.Path(exists=True), default=".", help="Workspace root directory")
@click.option("--dry-run", is_flag=True, help="Show what would be done without executing")
def migrate(workspace: str, dry_run: bool) -> None:
    """
    Migrate completed phases from active/ to completed/ folder.
    
    Example:
        cortex-cleanup-migrate --dry-run
        cortex-cleanup-migrate  # Execute
    """
    workspace_path = Path(workspace).resolve()
    auditor = CleanupAuditor(workspace_path)
    
    # Discover completed phases
    completed_phases = auditor.audit_completed_phases()
    
    click.echo(f"Found {len(completed_phases)} completed phases to migrate")
    
    if not completed_phases:
        click.echo("✅ No phases to migrate")
        return
    
    # Ensure completed/ directory exists
    if not dry_run:
        auditor.completed_phases_dir.mkdir(parents=True, exist_ok=True)
    
    # Migrate each phase
    for phase_id in completed_phases:
        yaml_file = auditor.active_phases_dir / f"{phase_id.lower()}.yaml"
        
        if not yaml_file.exists():
            # Try without lowercase
            yaml_file = auditor.active_phases_dir / f"{phase_id}.yaml"
        
        if yaml_file.exists():
            target_file = auditor.completed_phases_dir / yaml_file.name
            
            if dry_run:
                click.echo(f"Would migrate: {yaml_file.name} → completed/")
            else:
                yaml_file.rename(target_file)
                click.echo(f"✅ Migrated: {yaml_file.name}")


if __name__ == "__main__":
    cli()

# AC_COMPLETE: AC-WAVE-J-001 ✅
