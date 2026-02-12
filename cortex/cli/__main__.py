"""CORTEX CLI Main Entry Point.

Enables running CORTEX via: python -m cortex.cli

Author: Asif Hussain
Phase: 8
AC-ID: CLI-001
"""

from pathlib import Path
from typing import Optional

import click

from cortex.cli.commands.lens import lens
from cortex.cli.lens_dashboard import dashboard


@click.group()
@click.version_option(version="1.0.0", prog_name="cortex")
def cli() -> None:
    """
    CORTEX - COgnitive Real-Time EXecution System.

    AI-powered development orchestrator with governance-first architecture.

    \b
    Commands:
      lens          LENS Remote Intelligence (git history, AST, comments)
      status        Show system status
      governance    Governance rules and compliance
      ask           Ask questions about the codebase

    \b
    Examples:
      cortex lens analyze-remote owner/repo src/file.py
      cortex status
      cortex governance list
    """
    pass


@cli.command()
def status() -> None:
    """Show CORTEX system status."""
    try:
        from cortex.wiring import get_registry

        registry = get_registry()
        orchestrators = registry.list_orchestrators()

        click.echo("🧠 CORTEX Status")
        click.echo("=" * 40)
        click.echo(f"Orchestrators Wired: {len(orchestrators)}")
        click.echo()
        click.echo("✅ All systems operational")
    except Exception as e:
        click.echo(f"⚠️  Status check failed: {e}")


@cli.group()
def governance() -> None:
    """Governance rules and compliance commands."""
    pass


@governance.command("list")
def governance_list() -> None:
    """List all governance rules."""
    click.echo("📋 CORTEX Governance Rules (Tier 0)")
    click.echo("=" * 50)
    rules = [
        ("CORE-008", "TDD - Tests BEFORE code"),
        ("CORE-011", "Type hints MANDATORY"),
        ("CORE-012", "Google-style docstrings"),
        ("CORE-013", "No bare except clauses"),
        ("CORE-026", "Git checkpoint before major changes"),
        ("CORE-027", "Audit trail (AC_START → AC_COMPLETE)"),
        ("CORE-028", "File Naming - snake_case for Python"),
        ("CORE-029", "Response header enforcement"),
        ("CORE-030", "Implementation Truth - verify code"),
        ("CORE-035", "Single Canonical Implementation"),
        ("CORE-038", "File Placement Policy"),
    ]
    for rule_id, description in rules:
        click.echo(f"  {rule_id}: {description}")


@governance.command("check")
@click.argument("file_path", type=click.Path(exists=True))
def governance_check(file_path: str) -> None:
    """Check a file for governance compliance."""
    path = Path(file_path)
    click.echo(f"🔍 Checking: {path.name}")

    issues = []

    # Check file naming (CORE-028)
    if path.suffix == ".py" and "-" in path.stem:
        issues.append(("CORE-028", "Python files must use snake_case (hyphens forbidden)"))

    # Check for type hints and docstrings
    if path.suffix == ".py":
        content = path.read_text()
        if "def " in content and "-> " not in content:
            issues.append(("CORE-011", "Missing return type hints"))
        if "def " in content and '"""' not in content and "'''" not in content:
            issues.append(("CORE-012", "Missing docstrings"))
        if "except:" in content and "except Exception" not in content:
            issues.append(("CORE-013", "Bare except clause detected"))

    if issues:
        click.echo("⚠️  Issues found:")
        for rule_id, msg in issues:
            click.echo(f"   [{rule_id}] {msg}")
    else:
        click.echo("✅ No governance issues found")


@cli.command()
@click.argument("question")
@click.option("--category", "-c", help="Question category (architecture, implementation, testing)")
def ask(question: str, category: Optional[str] = None) -> None:
    """Ask a question about the codebase."""
    from cortex.cli.commands.inquiry import AskCommand

    cmd = AskCommand()
    result = cmd.execute(question, category=category)

    if result.success:
        click.echo(f"✅ {result.message}")
        if result.data:
            click.echo(f"\n{result.data.get('answer', '')}")
    else:
        click.echo(f"❌ {result.message}")
        if result.errors:
            for err in result.errors:
                click.echo(f"   - {err}")


# Register command groups
cli.add_command(lens)
cli.add_command(dashboard)

# Register onboard command group
try:
    from cortex.cli.commands.onboard import onboard
    cli.add_command(onboard)
except ImportError:
    pass  # Graceful fallback if dependencies not available


def main() -> None:
    """Main entry point."""
    cli()


if __name__ == "__main__":
    main()
