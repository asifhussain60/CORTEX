"""
LENS Dashboard CLI Commands.

Provides CLI interface for generating and serving CORTEX LENS dashboards.

AC-ID: LENS-DASH-014
Author: Asif Hussain
Phase: 14
"""

from pathlib import Path
from typing import Optional

import click
import uvicorn

from cortex.orchestrators.support.lens_visualization_orchestrator import (
    LENSVisualizationOrchestrator,
)


# Configuration
DASHBOARD_ROOT = Path.cwd() / ".cortex" / "lens-dashboard"


@click.group()
def dashboard() -> None:
    """
    CORTEX LENS Dashboard commands.

    Generate and serve interactive visual intelligence dashboards for code repositories.
    """
    pass


@dashboard.command()
@click.argument(
    "repository_path",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    required=False,
    default=None,
)
@click.option(
    "--output",
    "-o",
    type=click.Path(path_type=Path),
    help="Custom output directory for dashboard",
    default=None,
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Enable verbose output",
)
def generate(
    repository_path: Optional[Path],
    output: Optional[Path],
    verbose: bool,
) -> None:
    """
    Generate LENS dashboard for a repository.

    If REPOSITORY_PATH is not provided, uses current directory.

    Example:
        cortex lens dashboard generate /path/to/repo
        cortex lens dashboard generate --output /custom/path
        cortex lens dashboard generate  # Uses current directory
    """
    # Use current directory if path not provided
    if repository_path is None:
        repository_path = Path.cwd()

    click.echo(f"🧠 CORTEX LENS Dashboard Generator")
    click.echo(f"Repository: {repository_path}")

    if verbose:
        click.echo(f"Output: {output or 'auto'}")

    try:
        # Validate repository path
        if not repository_path.exists():
            click.echo(
                click.style(
                    f"❌ Error: Repository path not found: {repository_path}",
                    fg="red",
                ),
                err=True,
            )
            raise click.Abort()

        # Initialize orchestrator
        if verbose:
            click.echo("Initializing LENS orchestrator...")

        orchestrator = LENSVisualizationOrchestrator(repo_path=repository_path)

        # Determine output path
        output_path = output or (DASHBOARD_ROOT / repository_path.name)

        if verbose:
            click.echo(f"Generating dashboard at {output_path}...")

        # Generate dashboard
        dashboard_path = orchestrator.generate_dashboard(output_dir=output_path)

        click.echo(
            click.style(
                f"✅ Dashboard generated successfully!",
                fg="green",
                bold=True,
            )
        )
        click.echo(f"📁 Location: {dashboard_path}")
        click.echo(f"\n🚀 To serve the dashboard, run:")
        click.echo(f"   cortex lens dashboard serve\n")

    except Exception as e:
        click.echo(
            click.style(
                f"❌ Error: Dashboard generation failed: {str(e)}",
                fg="red",
            ),
            err=True,
        )
        if verbose:
            import traceback
            click.echo(traceback.format_exc(), err=True)
        raise click.Abort()


@dashboard.command()
@click.option(
    "--host",
    "-h",
    default="127.0.0.1",
    help="Host to bind server to",
)
@click.option(
    "--port",
    "-p",
    default=8080,
    type=int,
    help="Port to bind server to",
)
@click.option(
    "--reload",
    is_flag=True,
    help="Enable auto-reload (development mode)",
)
def serve(host: str, port: int, reload: bool) -> None:
    """
    Serve LENS dashboard via HTTP server.

    Starts a local HTTP server to view dashboards in the browser.

    Example:
        cortex lens dashboard serve
        cortex lens dashboard serve --port 9000
        cortex lens dashboard serve --host 0.0.0.0 --port 8080
    """
    click.echo(f"🧠 CORTEX LENS Dashboard Server")
    click.echo(f"Host: {host}")
    click.echo(f"Port: {port}")
    click.echo(f"\n🚀 Starting server...")
    click.echo(f"📊 Dashboard URL: http://{host}:{port}/api/lens/dashboard/list")
    click.echo(f"\n⏹️  Press CTRL+C to stop\n")

    try:
        from cortex.visualization.api.dashboard_routes import app

        uvicorn.run(
            app,
            host=host,
            port=port,
            reload=reload,
            log_level="info",
        )
    except KeyboardInterrupt:
        click.echo("\n\n⏹️  Server stopped")
    except Exception as e:
        click.echo(
            click.style(
                f"❌ Error: Server failed to start: {str(e)}",
                fg="red",
            ),
            err=True,
        )
        raise click.Abort()


@dashboard.command(name="list")
def list_cmd() -> None:
    """
    List all available dashboards.

    Shows all generated dashboards in the default location.

    Example:
        cortex lens dashboard list
    """
    click.echo(f"🧠 CORTEX LENS Dashboard List")
    click.echo(f"Location: {DASHBOARD_ROOT}\n")

    if not DASHBOARD_ROOT.exists():
        click.echo("No dashboards found. Generate one with:")
        click.echo("  cortex lens dashboard generate <repository_path>")
        return

    dashboards = [d for d in DASHBOARD_ROOT.iterdir() if d.is_dir()]

    if not dashboards:
        click.echo("No dashboards found. Generate one with:")
        click.echo("  cortex lens dashboard generate <repository_path>")
        return

    click.echo(f"Found {len(dashboards)} dashboard(s):\n")
    for i, dashboard_dir in enumerate(sorted(dashboards), 1):
        # Check for metadata
        metadata_file = dashboard_dir / "metadata.json"
        if metadata_file.exists():
            import json
            try:
                with open(metadata_file) as f:
                    metadata = json.load(f)
                generated_at = metadata.get("generated_at", "Unknown")
                click.echo(f"  {i}. {dashboard_dir.name}")
                click.echo(f"     Generated: {generated_at}")
            except Exception:
                click.echo(f"  {i}. {dashboard_dir.name}")
        else:
            click.echo(f"  {i}. {dashboard_dir.name}")

    click.echo(f"\n🚀 To serve dashboards, run:")
    click.echo(f"   cortex lens dashboard serve\n")
