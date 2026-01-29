"""CLI Commands for LENS Dashboard.

Provides command-line interface for dashboard generation and management.

Commands:
    cortex lens dashboard generate <repo> - Generate dashboard
    cortex lens dashboard serve [port] - Start dashboard server
    cortex lens dashboard cache list - List cached dashboards
    cortex lens dashboard cache clear - Clear dashboard cache
    cortex lens vendor bundle - Download vendor assets

Integration:
    These commands integrate with the CORTEX CLI infrastructure and
    can be invoked via the main `cortex` command.
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


def cmd_generate(args: argparse.Namespace) -> int:
    """Generate dashboard for a repository.
    
    Args:
        args: Parsed command line arguments
        
    Returns:
        Exit code (0 for success)
    """
    from cortex_lens.backend.orchestrator import DashboardOrchestrator
    from cortex_lens.backend.cache_manager import CacheManager
    
    repo_path = Path(args.repo).resolve()
    
    if not repo_path.exists():
        logger.error(f"Repository not found: {repo_path}")
        return 1
    
    logger.info(f"🔍 Analyzing repository: {repo_path.name}")
    
    try:
        orchestrator = DashboardOrchestrator()
        dashboard = orchestrator.generate_dashboard(
            repo_path,
            force_refresh=args.force,
        )
        
        output_path = orchestrator.save_dashboard(dashboard)
        
        logger.info(f"✅ Dashboard generated successfully!")
        logger.info(f"   Repository: {dashboard.repo_name}")
        logger.info(f"   Type: {'CORTEX' if dashboard.is_cortex else 'External'}")
        logger.info(f"   Tabs: {len(dashboard.tabs)}")
        logger.info(f"   Output: {output_path}")
        
        if args.open:
            index_path = output_path / "index.html"
            if index_path.exists():
                webbrowser.open(f"file://{index_path}")
                logger.info(f"   Opened in browser")
        
        return 0
        
    except Exception as e:
        logger.error(f"❌ Dashboard generation failed: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


def cmd_serve(args: argparse.Namespace) -> int:
    """Start dashboard server.
    
    Args:
        args: Parsed command line arguments
        
    Returns:
        Exit code (0 for success)
    """
    port = args.port
    directory = args.directory
    
    if directory:
        directory = Path(directory).resolve()
        if not directory.exists():
            logger.error(f"Directory not found: {directory}")
            return 1
    else:
        # Default to cortex-lens folder
        directory = Path(__file__).parent.parent
    
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
            logger.info(f"🚀 LENS Dashboard Server")
            logger.info(f"   Serving: {directory}")
            logger.info(f"   URL: http://localhost:{port}")
            logger.info(f"   Press Ctrl+C to stop")
            logger.info("")
            
            if args.open:
                webbrowser.open(f"http://localhost:{port}")
            
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
    """List cached dashboards.
    
    Args:
        args: Parsed command line arguments
        
    Returns:
        Exit code (0 for success)
    """
    from cortex_lens.backend.cache_manager import get_cache_manager
    
    cache_manager = get_cache_manager()
    entries = cache_manager.list_cached()
    
    if not entries:
        logger.info("No cached dashboards found")
        return 0
    
    logger.info(f"📦 Cached Dashboards ({len(entries)}):")
    logger.info("")
    
    for entry in entries:
        status = "⚠️  expired" if entry.is_expired() else "✓"
        repo_type = "CORTEX" if entry.is_cortex else "external"
        logger.info(f"  {status} {Path(entry.repo_path).name} ({repo_type})")
        logger.info(f"      Path: {entry.repo_path}")
        logger.info(f"      Output: {entry.output_path}")
        logger.info(f"      Created: {entry.created_at.strftime('%Y-%m-%d %H:%M')}")
        logger.info("")
    
    return 0


def cmd_cache_clear(args: argparse.Namespace) -> int:
    """Clear dashboard cache.
    
    Args:
        args: Parsed command line arguments
        
    Returns:
        Exit code (0 for success)
    """
    from cortex_lens.backend.cache_manager import get_cache_manager
    
    cache_manager = get_cache_manager()
    
    if args.all:
        # Clear all cache
        removed = cache_manager.cleanup_old_dashboards(max_age_days=0)
        logger.info(f"🗑️  Cleared {removed} cached dashboards")
    elif args.expired:
        # Clear only expired
        removed = cache_manager.cleanup_expired()
        logger.info(f"🗑️  Cleared {removed} expired cache entries")
    elif args.repo:
        # Clear specific repo
        success = cache_manager.invalidate(Path(args.repo))
        if success:
            logger.info(f"🗑️  Cleared cache for {args.repo}")
        else:
            logger.info(f"No cache entry found for {args.repo}")
    else:
        logger.error("Specify --all, --expired, or --repo")
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
        help="Generate dashboard for a repository",
    )
    gen_parser.add_argument(
        "repo",
        type=str,
        help="Path to the repository to analyze",
    )
    gen_parser.add_argument(
        "--force", "-f",
        action="store_true",
        help="Force regeneration (ignore cache)",
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
        "--directory", "-d",
        type=str,
        help="Directory to serve (default: cortex-lens/)",
    )
    serve_parser.add_argument(
        "--open", "-o",
        action="store_true",
        help="Open in browser",
    )
    serve_parser.set_defaults(func=cmd_serve)
    
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
        "--expired", "-e",
        action="store_true",
        help="Clear only expired entries",
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
