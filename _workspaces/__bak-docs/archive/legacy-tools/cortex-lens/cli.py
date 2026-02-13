"""CLI Commands for LENS Dashboard.

Provides command-line interface for dashboard generation and management.

Commands:
    cortex lens generate <repo> [--cortex] - Generate dashboard JSON files
    cortex lens serve [--port] - Start dashboard server
    cortex lens open - Open dashboard in browser

Integration:
    These commands integrate with the CORTEX CLI infrastructure and
    can be invoked via the main `cortex` command.

Architecture:
    Static HTML + JSON (no FastAPI required for viewing)
    - lens-dashboard.html: Main entry point with repository tiles
    - cortex-dashboard.html: 8-tab analysis dashboard
    - data/*.json: Pre-generated dashboard data
"""

import argparse
import http.server
import json
import logging
import socketserver
import sys
import webbrowser
from pathlib import Path
from typing import List, Optional

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


# ============================================================================
# GENERATE COMMAND - Uses LENSDashboardOrchestrator
# ============================================================================

def cmd_generate(args: argparse.Namespace) -> int:
    """Generate dashboard JSON files for a repository.
    
    Uses LENSDashboardOrchestrator to analyze the repository and generate
    JSON data files for all dashboard tabs.
    
    Args:
        args: Parsed command line arguments
        
    Returns:
        Exit code (0 for success)
    """
    # Add project root to path for imports
    project_root = Path(__file__).parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    
    from cortex.orchestrators.support.lens_dashboard_orchestrator import (
        get_lens_dashboard_orchestrator
    )
    
    repo_path = Path(args.repo).resolve()
    
    if not repo_path.exists():
        logger.error(f"❌ Repository not found: {repo_path}")
        return 1
    
    is_cortex = getattr(args, 'cortex', False) or _detect_cortex(repo_path)
    
    logger.info(f"")
    logger.info(f"🔍 LENS Dashboard Generator")
    logger.info(f"   Repository: {repo_path.name}")
    logger.info(f"   Type: {'CORTEX (8 tabs)' if is_cortex else 'External (5 tabs)'}")
    logger.info(f"")
    
    try:
        orchestrator = get_lens_dashboard_orchestrator()
        result = orchestrator.generate_for_repo(
            repo_path=repo_path,
            repo_name=repo_path.name,
            is_cortex=is_cortex
        )
        
        if result.get("success"):
            logger.info(f"✅ Dashboard data generated successfully!")
            logger.info(f"   Files: {', '.join(result['files_generated'])}")
            logger.info(f"   Output: {result['data_dir']}")
            logger.info(f"")
            logger.info(f"📊 View your dashboard:")
            logger.info(f"   Run: cortex lens serve")
            
            if args.open:
                serve_and_open()
            
            return 0
        else:
            logger.error(f"❌ Generation failed: {result.get('error', 'Unknown error')}")
            return 1
        
    except Exception as e:
        logger.error(f"❌ Dashboard generation failed: {e}")
        if getattr(args, 'verbose', False):
            import traceback
            traceback.print_exc()
        return 1


def _detect_cortex(repo_path: Path) -> bool:
    """Detect if repository is CORTEX based on markers."""
    markers = [
        repo_path / "cortex",
        repo_path / "cortex_brain",
        repo_path / ".github" / "copilot-instructions.md"
    ]
    return any(m.exists() for m in markers)


def serve_and_open() -> None:
    """Start server and open browser."""
    import subprocess
    import time
    
    lens_dir = Path(__file__).parent
    subprocess.Popen(
        ["python", "-m", "http.server", "8080"],
        cwd=lens_dir,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    time.sleep(1)
    webbrowser.open("http://localhost:8080/lens-dashboard.html")


def cmd_open(args: argparse.Namespace) -> int:
    """Open dashboard in browser (starts server in background).
    
    Args:
        args: Parsed command line arguments
        
    Returns:
        Exit code (0 for success)
    """
    import subprocess
    import time
    
    port = getattr(args, 'port', 8080)
    lens_dir = Path(__file__).parent
    
    logger.info(f"")
    logger.info(f"🚀 Starting LENS Dashboard...")
    
    # Start server in background
    subprocess.Popen(
        ["python", "-m", "http.server", str(port)],
        cwd=lens_dir,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    
    time.sleep(1)
    
    url = f"http://localhost:{port}/lens-dashboard.html"
    webbrowser.open(url)
    
    logger.info(f"   Opened: {url}")
    logger.info(f"   Server running on port {port}")
    logger.info(f"")
    
    return 0


# ============================================================================
# SERVE COMMAND - Static file server
# ============================================================================


def cmd_serve(args: argparse.Namespace) -> int:
    """Start dashboard server.
    
    Args:
        args: Parsed command line arguments
        
    Returns:
        Exit code (0 for success)
    """
    port = args.port
    
    # Always serve from cortex-lens folder
    directory = Path(__file__).parent
    
    # Change to serve directory
    import os
    os.chdir(directory)
    
    # Create handler with CORS headers
    class CORSHandler(http.server.SimpleHTTPRequestHandler):
        def end_headers(self):
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")
            super().end_headers()
        
        def log_message(self, format, *args):
            if not self.path.endswith((".js", ".css", ".png", ".ico")):
                logger.info(f"  {args[0]}")
    
    try:
        with socketserver.TCPServer(("", port), CORSHandler) as httpd:
            logger.info(f"")
            logger.info(f"🚀 LENS Dashboard Server")
            logger.info(f"   Directory: {directory}")
            logger.info(f"")
            logger.info(f"   📊 Dashboard: http://localhost:{port}/lens-dashboard.html")
            logger.info(f"   🔬 CORTEX:    http://localhost:{port}/cortex-dashboard.html?repo=cortex")
            logger.info(f"")
            logger.info(f"   Press Ctrl+C to stop")
            logger.info("")
            
            if args.open:
                webbrowser.open(f"http://localhost:{port}/lens-dashboard.html")
            
            httpd.serve_forever()
            
    except KeyboardInterrupt:
        logger.info("\n👋 Server stopped")
        return 0
    except OSError as e:
        if "Address already in use" in str(e):
            logger.error(f"❌ Port {port} is already in use")
        else:
            logger.error(f"❌ Server error: {e}")
        return 1


def cmd_cache_list(args: argparse.Namespace) -> int:
    """List generated dashboard data.
    
    Args:
        args: Parsed command line arguments
        
    Returns:
        Exit code (0 for success)
    """
    data_dir = Path(__file__).parent / "data"
    
    if not data_dir.exists():
        logger.info("No dashboard data found")
        return 0
    
    logger.info(f"📦 Generated Dashboard Data:")
    logger.info("")
    
    # CORTEX data
    cortex_dir = data_dir / "cortex"
    if cortex_dir.exists():
        files = list(cortex_dir.glob("*.json"))
        logger.info(f"  ✓ CORTEX ({len(files)} files)")
        for f in files:
            logger.info(f"      - {f.name}")
        logger.info("")
    
    # External repos
    repos_dir = data_dir / "repos"
    if repos_dir.exists():
        for repo_dir in repos_dir.iterdir():
            if repo_dir.is_dir():
                files = list(repo_dir.glob("*.json"))
                logger.info(f"  ✓ {repo_dir.name} ({len(files)} files)")
    
    return 0


def cmd_cache_clear(args: argparse.Namespace) -> int:
    """Clear dashboard data cache.
    
    Args:
        args: Parsed command line arguments
        
    Returns:
        Exit code (0 for success)
    """
    import shutil
    
    data_dir = Path(__file__).parent / "data"
    
    if args.all:
        # Clear all external repo data (keep cortex)
        repos_dir = data_dir / "repos"
        if repos_dir.exists():
            for repo_dir in repos_dir.iterdir():
                if repo_dir.is_dir() and repo_dir.name != "repos.json":
                    shutil.rmtree(repo_dir)
                    logger.info(f"🗑️  Cleared {repo_dir.name}")
        logger.info("✅ Cache cleared")
    elif args.repo:
        # Clear specific repo
        repo_dir = data_dir / "repos" / args.repo.lower().replace(" ", "-")
        if repo_dir.exists():
            shutil.rmtree(repo_dir)
            logger.info(f"🗑️  Cleared cache for {args.repo}")
        else:
            logger.info(f"No cache entry found for {args.repo}")
    else:
        logger.error("Specify --all or --repo")
        return 1
    
    return 0


def cmd_vendor_bundle(args: argparse.Namespace) -> int:
    """Download and bundle vendor assets.
    
    Args:
        args: Parsed command line arguments
        
    Returns:
        Exit code (0 for success)
    """
    from cortex.visualization.scripts.bundle_vendor_assets import (
        bundle_vendor_assets,
        verify_vendor_assets,
    )
    
    if args.verify:
        logger.info("🔍 Verifying vendor assets...")
        results = verify_vendor_assets()
        
        all_present = all(results.values())
        for name, present in results.items():
            status = "✓" if present else "✗"
            logger.info(f"  {status} {name}")
        
        if all_present:
            logger.info("\n✅ All vendor assets present")
            return 0
        else:
            logger.info("\n⚠️  Some assets missing. Run 'cortex lens vendor bundle' to download.")
            return 1
    else:
        logger.info("📦 Bundling vendor assets for offline operation...")
        results = bundle_vendor_assets()
        
        all_success = all(results.values())
        return 0 if all_success else 1


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser for LENS Dashboard CLI.
    
    Returns:
        Configured ArgumentParser
    """
    parser = argparse.ArgumentParser(
        prog="cortex lens dashboard",
        description="LENS Dashboard - Visual Intelligence for Code Repositories",
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Generate command
    gen_parser = subparsers.add_parser(
        "generate",
        help="Generate dashboard JSON data for a repository",
    )
    gen_parser.add_argument(
        "repo",
        type=str,
        help="Path to the repository to analyze",
    )
    gen_parser.add_argument(
        "--cortex", "-c",
        action="store_true",
        help="Generate full 8-tab CORTEX dashboard (auto-detected)",
    )
    gen_parser.add_argument(
        "--open", "-o",
        action="store_true",
        help="Open dashboard in browser after generation",
    )
    gen_parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show verbose output",
    )
    gen_parser.set_defaults(func=cmd_generate)
    
    # Serve command
    serve_parser = subparsers.add_parser(
        "serve",
        help="Start dashboard server",
    )
    serve_parser.add_argument(
        "--port", "-p",
        type=int,
        default=8080,
        help="Port to serve on (default: 8080)",
    )
    serve_parser.add_argument(
        "--open", "-o",
        action="store_true",
        help="Open in browser",
    )
    serve_parser.set_defaults(func=cmd_serve)
    
    # Open command (shortcut)
    open_parser = subparsers.add_parser(
        "open",
        help="Open dashboard in browser (starts server if needed)",
    )
    open_parser.add_argument(
        "--port", "-p",
        type=int,
        default=8080,
        help="Port to serve on (default: 8080)",
    )
    open_parser.set_defaults(func=cmd_open)
    
    # Cache commands
    cache_parser = subparsers.add_parser(
        "cache",
        help="Manage dashboard cache",
    )
    cache_subparsers = cache_parser.add_subparsers(dest="cache_command")
    
    # Cache list
    cache_list = cache_subparsers.add_parser(
        "list",
        help="List cached dashboards",
    )
    cache_list.set_defaults(func=cmd_cache_list)
    
    # Cache clear
    cache_clear = cache_subparsers.add_parser(
        "clear",
        help="Clear dashboard cache",
    )
    cache_clear.add_argument(
        "--all", "-a",
        action="store_true",
        help="Clear all cached dashboards",
    )
    cache_clear.add_argument(
        "--repo", "-r",
        type=str,
        help="Clear cache for specific repository",
    )
    cache_clear.set_defaults(func=cmd_cache_clear)
    
    # Vendor command
    vendor_parser = subparsers.add_parser(
        "vendor",
        help="Manage vendor assets",
    )
    vendor_subparsers = vendor_parser.add_subparsers(dest="vendor_command")
    
    # Vendor bundle
    vendor_bundle = vendor_subparsers.add_parser(
        "bundle",
        help="Download and bundle vendor assets",
    )
    vendor_bundle.add_argument(
        "--verify",
        action="store_true",
        help="Only verify assets are present",
    )
    vendor_bundle.set_defaults(func=cmd_vendor_bundle)
    
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    """Main CLI entry point.
    
    Args:
        argv: Optional argument list (defaults to sys.argv)
        
    Returns:
        Exit code
    """
    parser = create_parser()
    args = parser.parse_args(argv)
    
    if not args.command:
        parser.print_help()
        return 0
    
    if hasattr(args, "func"):
        return args.func(args)
    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())
