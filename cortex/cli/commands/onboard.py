"""
Universal Repository Onboarding CLI Command.

Provides CLI interface for the universal repository onboarding system:
- Onboard any repository
- Generate glassmorphism dashboard
- Update landing page hub
- Security assessment and business narratives

Authority: CORE-011 (type hints), CORE-012 (docstrings)
AC-ID: AC-UNIVERSAL-ONBOARD-CLI-001
"""

from pathlib import Path
from typing import Optional

import click


@click.group()
def onboard() -> None:
    """Universal repository onboarding commands."""
    pass


@onboard.command("repo")
@click.argument("path", type=click.Path(exists=True))
@click.option("--name", "-n", help="Override repository name")
@click.option("--icon", "-i", default="📁", help="Emoji icon for landing page tile")
@click.option("--no-dashboard", is_flag=True, help="Skip dashboard generation")
@click.option("--no-domain-update", is_flag=True, help="Skip company domain update")
@click.option("--output", "-o", type=click.Path(), help="Custom dashboard output path")
def onboard_repo(
    path: str,
    name: Optional[str],
    icon: str,
    no_dashboard: bool,
    no_domain_update: bool,
    output: Optional[str],
) -> None:
    """
    Onboard a repository with comprehensive analysis.

    Analyzes the repository, generates a glassmorphism dashboard with
    confidence scoring, and updates the landing page hub.

    Examples:
        cortex onboard repo /path/to/kashkole
        cortex onboard repo ./my-project --name "my-app" --icon "💼"
        cortex onboard repo /path/to/repo --no-dashboard

    Output:
        - Dashboard: company/dashboards/{name}/dashboard.html
        - Landing:   company/dashboards/index.html
        - Analysis:  Console output with confidence scores
    """
    from cortex.orchestrators.support.repository_onboarding_orchestrator import (
        get_repository_onboarding_orchestrator,
    )

    repo_path = Path(path).resolve()

    click.echo("\n🧠 CORTEX Universal Onboarding")
    click.echo("=" * 50)
    click.echo(f"Repository: {repo_path}")
    click.echo(f"Name: {name or repo_path.name}")
    click.echo(f"Icon: {icon}")
    click.echo("=" * 50 + "\n")

    try:
        orchestrator = get_repository_onboarding_orchestrator()

        result = orchestrator.onboard_repository(
            repo_path=repo_path,
            include_dashboard=not no_dashboard,
            update_company_domain=not no_domain_update,
            repo_name=name,
            icon=icon,
        )

        if result.success:
            click.echo("\n✅ Onboarding Complete!")
            click.echo("-" * 40)

            # Business narrative summary
            if result.business_narrative:
                narrative = result.business_narrative
                click.echo(f"\n📋 {getattr(narrative, 'title', 'Repository')}")
                click.echo(f"   {getattr(narrative, 'tagline', '')}")

                # Confidence
                confidence = getattr(narrative, 'confidence', None)
                if confidence:
                    score = getattr(confidence, 'score', 0)
                    level = getattr(confidence, 'level', 'low')
                    click.echo(f"\n🎯 Confidence: {score}% ({level})")

                # Use cases
                use_cases = getattr(narrative, 'use_cases', [])
                if use_cases:
                    click.echo(f"\n🎯 Use Cases ({len(use_cases)} detected):")
                    for uc in use_cases[:5]:
                        uc_title = getattr(uc, 'title', 'Unknown')
                        click.echo(f"   • {uc_title}")

            # Security summary
            security = result.security_risks
            p0 = len(security.get('p0_risks', []))
            p1 = len(security.get('p1_risks', []))
            p2 = len(security.get('p2_risks', []))

            click.echo("\n🔒 Security Summary:")
            if p0 > 0:
                click.echo(click.style(f"   ⛔ P0 Critical: {p0}", fg='red'))
            if p1 > 0:
                click.echo(click.style(f"   ⚠️  P1 High: {p1}", fg='yellow'))
            if p2 > 0:
                click.echo(click.style(f"   ℹ️  P2 Medium: {p2}", fg='blue'))
            if p0 == 0 and p1 == 0 and p2 == 0:
                click.echo(click.style("   ✅ No issues detected", fg='green'))

            # Output paths
            click.echo("\n📂 Output:")
            if result.dashboard_path:
                click.echo(f"   Dashboard: {result.dashboard_path}")
            if result.landing_page_path:
                click.echo(f"   Landing:   {result.landing_page_path}")

            click.echo("\n" + "=" * 50)
            click.echo("🎉 Repository onboarded successfully!")

        else:
            click.echo(click.style(f"\n❌ Onboarding Failed: {result.error}", fg='red'))
            raise click.Abort()

    except Exception as e:
        click.echo(click.style(f"\n❌ Error: {e}", fg='red'), err=True)
        raise click.Abort()


@onboard.command("list")
def list_repos() -> None:
    """
    List all onboarded repositories.

    Shows all repositories registered in the landing page hub
    with their status and last onboarding date.
    """
    from cortex.orchestrators.support.landing_page_generator import (
        get_landing_page_generator,
    )

    click.echo("\n🧠 CORTEX Onboarded Repositories")
    click.echo("=" * 50)

    try:
        generator = get_landing_page_generator()
        repos = generator.list_repos()

        if not repos:
            click.echo("No repositories onboarded yet.")
            click.echo("\nUse: cortex onboard repo /path/to/repo")
            return

        for repo in repos:
            name = repo.get('name', 'Unknown')
            icon = repo.get('icon', '📁')
            desc = repo.get('description', '')[:40]
            confidence = repo.get('confidence', 0)
            date = repo.get('onboarded_at', 'Unknown')[:10]

            click.echo(f"\n{icon} {name.upper()}")
            click.echo(f"   {desc}")
            click.echo(f"   Confidence: {confidence}% | Onboarded: {date}")

        click.echo("\n" + "=" * 50)
        click.echo(f"Total: {len(repos)} repositories")

    except Exception as e:
        click.echo(click.style(f"Error: {e}", fg='red'), err=True)


@onboard.command("remove")
@click.argument("name")
@click.option("--delete-files", is_flag=True, help="Also delete dashboard files")
def remove_repo(name: str, delete_files: bool) -> None:
    """
    Remove a repository from the landing page hub.

    Removes the repository tile from the landing page.
    Optionally deletes the dashboard files.

    Examples:
        cortex onboard remove kashkole
        cortex onboard remove my-app --delete-files
    """
    import shutil

    from cortex.orchestrators.support.landing_page_generator import (
        get_landing_page_generator,
    )

    click.echo(f"\n🧠 CORTEX Remove Repository: {name}")
    click.echo("=" * 50)

    try:
        generator = get_landing_page_generator()

        if generator.remove_repo_from_registry(name):
            click.echo(f"✅ Removed {name} from registry")
            generator.regenerate_landing_page()
            click.echo("✅ Landing page updated")

            if delete_files:
                dashboard_dir = generator.dashboards_root / name
                if dashboard_dir.exists():
                    shutil.rmtree(dashboard_dir)
                    click.echo(f"✅ Deleted: {dashboard_dir}")

            click.echo("\n🎉 Repository removed successfully!")
        else:
            click.echo(click.style(f"Repository '{name}' not found in registry", fg='yellow'))

    except Exception as e:
        click.echo(click.style(f"Error: {e}", fg='red'), err=True)


@onboard.command("regenerate")
def regenerate_landing() -> None:
    """
    Regenerate the landing page hub.

    Re-creates the landing page from the registry,
    useful after manual registry edits.
    """
    from cortex.orchestrators.support.landing_page_generator import (
        get_landing_page_generator,
    )

    click.echo("\n🧠 CORTEX Regenerate Landing Page")
    click.echo("=" * 50)

    try:
        generator = get_landing_page_generator()
        path = generator.regenerate_landing_page()
        click.echo(f"✅ Landing page regenerated: {path}")

    except Exception as e:
        click.echo(click.style(f"Error: {e}", fg='red'), err=True)
