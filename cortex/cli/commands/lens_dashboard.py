"""
LENS Dashboard CLI Commands.

Commands:
- cortex lens dashboard serve [--port 8888] [--no-browser]
- cortex lens dashboard serve cortex (CORTEX-specific view)
- cortex lens dashboard generate --repo <path> [--output <dir>]
- cortex lens dashboard clean --directory <dir> --older-than <days> [--dry-run]

Authority: CORE-008 (TDD), CORE-011 (Type hints), CORE-012 (Docstrings)
Phase: 14 - LENS Dashboard Implementation
AC-ID: LENS-DASH-015
"""

import click
import webbrowser
import time
from pathlib import Path
from typing import Optional
from datetime import datetime, timedelta


@click.group(name='dashboard')
def dashboard() -> None:
    """
    LENS Dashboard commands.
    
    Provides commands to serve, generate, and manage LENS dashboards.
    """
    pass


@dashboard.command(name='serve')
@click.argument('repo_name', required=False, default=None)
@click.option('--port', '-p', default=8888, type=int, help='Port to serve on (default: 8888)')
@click.option('--no-browser', is_flag=True, help='Do not open browser automatically')
@click.option('--host', default='127.0.0.1', help='Host to bind to (default: 127.0.0.1)')
def serve(repo_name: Optional[str], port: int, no_browser: bool, host: str) -> None:
    """
    Start LENS Dashboard server.
    
    Usage:
        cortex lens dashboard serve [--port 8888]
        cortex lens dashboard serve cortex (direct to CORTEX repo)
    
    Args:
        repo_name: Optional repository name (e.g., 'cortex' for CORTEX repo)
        port: Port to serve on
        no_browser: If True, don't open browser automatically
        host: Host to bind to
    """
    import uvicorn
    from fastapi import FastAPI
    from cortex.api.endpoints.lens_dashboard_routes import create_dashboard_router
    
    # Create FastAPI app
    app = FastAPI(
        title="CORTEX LENS Dashboard",
        description="Interactive code intelligence dashboard",
        version="1.0.0"
    )
    
    # Mount dashboard router
    router = create_dashboard_router()
    app.include_router(router, prefix="/api")
    
    # Add static file serving for templates
    from fastapi.staticfiles import StaticFiles
    from fastapi.responses import FileResponse
    
    templates_dir = Path(__file__).parent.parent.parent / "visualization" / "templates"
    
    @app.get("/")
    def root():
        """Serve main dashboard HTML."""
        if repo_name and repo_name.lower() == 'cortex':
            # Redirect to CORTEX repository view
            cortex_path = Path.cwd()
            return FileResponse(templates_dir / "dashboard.html")
        return FileResponse(templates_dir / "dashboard.html")
    
    # Build URL
    base_url = f"http://{host}:{port}"
    
    if repo_name and repo_name.lower() == 'cortex':
        # CORTEX-specific URL
        cortex_path = Path.cwd()
        url = f"{base_url}/?repo={cortex_path}"
        click.echo(f"🧠 Starting CORTEX LENS Dashboard for CORTEX repository...")
    else:
        url = base_url
        click.echo(f"🧠 Starting LENS Dashboard server...")
    
    click.echo(f"📊 Dashboard: {url}")
    click.echo(f"🔌 API: {base_url}/api/dashboard")
    click.echo(f"❤️  Health: {base_url}/api/dashboard/health")
    
    # Open browser
    if not no_browser:
        time.sleep(1.5)  # Give server time to start
        click.echo(f"🌐 Opening browser...")
        webbrowser.open(url)
    
    # Start server
    uvicorn.run(app, host=host, port=port, log_level="info")


@dashboard.command(name='generate')
@click.option('--repo', '-r', required=True, type=click.Path(exists=True), help='Repository path')
@click.option('--output', '-o', default='./company/dashboards/lens', type=click.Path(), help='Output directory')
def generate(repo: str, output: str) -> None:
    """
    Generate static HTML dashboard.
    
    Usage:
        cortex lens dashboard generate --repo /path/to/repo
        cortex lens dashboard generate --repo . --output ./my-dashboards
    
    Args:
        repo: Path to repository to analyze
        output: Output directory for generated HTML
    """
    from cortex.api.endpoints.lens_dashboard_routes import analyze_repository
    import json
    
    repo_path = Path(repo).resolve()
    output_path = Path(output)
    output_path.mkdir(parents=True, exist_ok=True)
    
    click.echo(f"🔍 Analyzing repository: {repo_path}")
    
    # Analyze repository
    try:
        data = analyze_repository(repo_path=str(repo_path))
        
        # Generate filename
        repo_name = repo_path.name
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        html_file = output_path / f"{repo_name}_dashboard_{timestamp}.html"
        json_file = output_path / f"{repo_name}_data_{timestamp}.json"
        
        # Save data as JSON
        with open(json_file, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        
        click.echo(f"💾 Data saved: {json_file}")
        
        # Generate HTML (simple template for now)
        templates_dir = Path(__file__).parent.parent.parent / "visualization" / "templates"
        dashboard_template = templates_dir / "dashboard.html"
        
        if dashboard_template.exists():
            html_content = dashboard_template.read_text()
            # Inject data into HTML
            html_content = html_content.replace(
                '</body>',
                f'<script>window.LENS_DATA = {json.dumps(data, default=str)};</script></body>'
            )
            html_file.write_text(html_content)
            click.echo(f"📄 Dashboard generated: {html_file}")
        else:
            click.echo(f"⚠️  Template not found, JSON only saved")
        
        click.echo(f"✅ Generation complete!")
        
    except Exception as e:
        click.echo(f"❌ Error: {str(e)}", err=True)
        raise click.Abort()


@dashboard.command(name='clean')
@click.option('--directory', '-d', default='./company/dashboards/lens', type=click.Path(exists=True), 
              help='Dashboard directory to clean')
@click.option('--older-than', '-o', default=30, type=int, 
              help='Remove dashboards older than N days (default: 30)')
@click.option('--dry-run', is_flag=True, help='Show what would be deleted without deleting')
def clean(directory: str, older_than: int, dry_run: bool) -> None:
    """
    Clean old dashboard files.
    
    Usage:
        cortex lens dashboard clean
        cortex lens dashboard clean --older-than 7
        cortex lens dashboard clean --dry-run
    
    Args:
        directory: Directory containing dashboards
        older_than: Remove files older than this many days
        dry_run: If True, show what would be deleted without deleting
    """
    import time
    
    dir_path = Path(directory)
    
    if not dir_path.exists():
        click.echo(f"📁 Directory does not exist: {dir_path}")
        return
    
    threshold = time.time() - (older_than * 24 * 60 * 60)
    
    click.echo(f"🧹 Cleaning dashboards in: {dir_path}")
    click.echo(f"📅 Removing files older than {older_than} days")
    
    if dry_run:
        click.echo(f"🔍 DRY RUN - No files will be deleted")
    
    deleted_count = 0
    total_size = 0
    
    # Find and remove old files
    for file_path in dir_path.glob("*dashboard*.html"):
        file_mtime = file_path.stat().st_mtime
        
        if file_mtime < threshold:
            file_size = file_path.stat().st_size
            total_size += file_size
            
            if dry_run:
                click.echo(f"  Would delete: {file_path.name} ({file_size} bytes)")
            else:
                file_path.unlink()
                click.echo(f"  Deleted: {file_path.name}")
            
            deleted_count += 1
    
    # Also clean JSON data files
    for file_path in dir_path.glob("*data*.json"):
        file_mtime = file_path.stat().st_mtime
        
        if file_mtime < threshold:
            file_size = file_path.stat().st_size
            total_size += file_size
            
            if dry_run:
                click.echo(f"  Would delete: {file_path.name} ({file_size} bytes)")
            else:
                file_path.unlink()
                click.echo(f"  Deleted: {file_path.name}")
            
            deleted_count += 1
    
    if deleted_count == 0:
        click.echo(f"✨ No files to clean")
    else:
        action = "Would delete" if dry_run else "Deleted"
        click.echo(f"✅ {action} {deleted_count} files ({total_size} bytes)")


# Export commands
__all__ = ['dashboard', 'serve', 'generate', 'clean']
