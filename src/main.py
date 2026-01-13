"""
CORTEX CLI Entry Point

Command-line interface for CORTEX AI Assistant.

Usage:
    # Interactive mode
    python -m src.main
    
    # Single command
    python -m src.main "help"
    python -m src.main "create tests for auth.py"
    
    # Setup mode
    python -m src.main --setup
    python -m src.main --setup --repo /path/to/repo
    
    # Format options
    python -m src.main "status" --format json
    python -m src.main "help" --format markdown
    
    # Verbose logging
    python -m src.main "implement feature" --verbose

Performance Optimization:
    - Fast-path routing for simple commands (help, version, status)
    - Lazy loading of heavy dependencies (tiers, agents, orchestrators)
    - Component caching for repeated invocations
    - Target: <50ms for fast commands, <1.7s for full initialization

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import sys
import argparse
import time
import logging
from pathlib import Path
from typing import Optional

# Fast-path handler loaded eagerly (lightweight)
from src.entry_point.fast_commands import FastCommandHandler, is_fast_command

# Header/Footer injection for CORTEX branding (AC-HEADER-001)
from src.infrastructure.response_header_footer_manager import wrap_cortex_response
from src.infrastructure.cortex_output_formatter import cortex_format, cortex_print

# CortexEntry loaded lazily (heavy)
from src.utils.lazy_loader import lazy_import

_entry_module = lazy_import('src.entry_point.cortex_entry')


def _is_phase8_operation(message: str) -> bool:
    """Check if message is a Phase 8 operation."""
    if not message:
        return False
    
    msg_lower = message.lower().strip()
    phase8_operations = [
        'integration-cleanup',
        'integration cleanup',
        'completion-report',
        'completion report',
        'phase8-status',
        'phase8 status',
        'phase 8 status'
    ]
    
    return any(op in msg_lower for op in phase8_operations)


def _handle_utility_command(command: str) -> str:
    """
    Handle fast utility commands (commit, align, healthcheck, optimize, deploy, system-maintenance).
    
    These commands bypass full CortexEntry initialization for speed.
    Context-aware operations automatically detect CORTEX repo vs user repo.
    
    Args:
        command: Utility command name (commit/align/healthcheck/optimize/deploy/system-maintenance)
    
    Returns:
        Formatted response text
    """
    try:
        # Import context detector
        from src.utils.context_detector import is_cortex_repo, get_context_type
        from pathlib import Path
        import os
        
        project_root = Path(os.getcwd())
        context_type = get_context_type(project_root)
        is_cortex = is_cortex_repo(project_root)
        
        if command == 'commit':
            # Commit always runs commit_push_sync orchestrator (git_checkpoint is TDD-only)
            from src.operations.commit_and_push import CommitAndPushOrchestrator
            orchestrator = CommitAndPushOrchestrator(repo_path=project_root)
            result = orchestrator.execute()
            if result.get('success'):
                return result.get('message', 'Commit and push complete')
            else:
                return f"[ERROR] {result.get('message', 'Commit failed')}"
        
        elif command == 'align':
            # Context-aware: admin version if in CORTEX repo, user version otherwise
            from src.operations.align import run_align
            
            if is_cortex:
                # Admin version: Full system alignment with all checks
                result = run_align(auto_fix=False, dry_run=False)
            else:
                # User version: Workspace alignment (will automatically skip admin-only checks)
                result = run_align(auto_fix=False, dry_run=False)
            
            return result.get('report_text', result.get('message', 'System alignment complete'))
        
        elif command == 'healthcheck':
            from src.operations.healthcheck import run_healthcheck
            result = run_healthcheck()
            # Format the response
            response = f"\n{'='*60}\nCORTEX Health Check Operation\n{'='*60}\n"
            response += result.get('message', 'Health check complete')
            if result.get('data'):
                response += "\n\nHealth Check Details:"
                for key, value in result['data'].items():
                    response += f"\n  {key}: {value}"
            return response
        
        elif command == 'optimize':
            # Context-aware: admin version if in CORTEX repo, user version otherwise
            if is_cortex:
                # Admin version: CORTEX optimization with SKULL tests
                from src.operations.modules.optimization.optimize_cortex_orchestrator import OptimizeCortexOrchestrator
                orchestrator = OptimizeCortexOrchestrator(project_root=project_root)
                result = orchestrator.execute(context={})
                return result.message
            else:
                # User version: Fast workspace optimization (skip SKULL tests)
                from src.operations.optimize import run_optimize
                result = run_optimize(skip_skull_tests=True)
                return result.get('message', 'Optimization complete')
        
        elif command == 'deploy':
            # Deploy is CORTEX-only operation (requires admin context)
            if not is_cortex:
                return "[ERROR] Deploy operation is only available in CORTEX repository. Run this command from the CORTEX development repository."
            
            # Run deploy with all 19 validation gates (no skipping allowed)
            from src.operations.deploy import run_deploy
            result = run_deploy(dry_run=False)
            if result.get('success'):
                return f"✅ Deployment complete\n   Branch: {result.get('branch', 'main')}\n   {result.get('validation', 'All 19 gates passed')}"
            else:
                return f"[ERROR] {result.get('message', 'Deployment failed')}"
        
        elif command == 'system-maintenance':
            # System maintenance is CORTEX-only operation
            if not is_cortex:
                return "[ERROR] System maintenance operation is only available in CORTEX repository. Run this command from the CORTEX development repository."
            
            # Run full system maintenance workflow
            from src.operations.modules.orchestration.system_maintenance_orchestrator import SystemMaintenanceOrchestrator
            orchestrator = SystemMaintenanceOrchestrator(project_root=project_root)
            result = orchestrator.execute(context={})
            
            if result.success:
                return f"✅ {result.message}\n\n{result.formatted_footer}"
            else:
                return f"[ERROR] {result.message}"
        
        else:
            return f"Unknown utility command: {command}"
    
    except Exception as e:
        import traceback
        return f"[ERROR] Utility command '{command}' failed: {e}\n{traceback.format_exc()}"


def _handle_phase8_operation(message: str, entry, args) -> str:
    """
    Handle Phase 8 operations (integration-cleanup, completion-report, phase8-status).
    
    Args:
        message: User command
        entry: CortexEntry instance
        args: Parsed CLI arguments
    
    Returns:
        Formatted response
    
    Note: Temporarily disabled - Phase8OperationHandler not yet implemented
    """
    # TODO: Re-enable when Phase8OperationHandler is implemented
    # from src.orchestrators.phase8_operation_handler import Phase8OperationHandler
    
    return "[INFO] Phase 8 operations temporarily disabled. Handler not yet implemented."
    
    # # Determine brain path - try multiple sources
    # if args.brain:
    #     brain_path = Path(args.brain)
    # elif hasattr(entry, 'config') and hasattr(entry.config, 'brain_path'):
    #     brain_path = entry.config.brain_path
    # else:
    #     # Fallback: auto-detect from current directory
    #     brain_path = Path.cwd() / "cortex-brain"
    # 
    # # Create handler with minimal dependencies
    # handler = Phase8OperationHandler(brain_path, logger=logging.getLogger(__name__))
    # 
    # msg_lower = message.lower().strip()
    # 
    # # Build context from CLI args
    # context = {
    #     'dry_run': getattr(args, 'dry_run', False),
    #     'profile': getattr(args, 'operation_profile', 'standard'),
    #     'output_path': getattr(args, 'output', None),
    #     'verbose': args.verbose,
    #     'format': args.format
    # }
    # 
    # # Route to appropriate handler
    # if 'integration-cleanup' in msg_lower or 'integration cleanup' in msg_lower:
    #     return handler.handle_integration_cleanup(context)
    # elif 'completion-report' in msg_lower or 'completion report' in msg_lower:
    #     return handler.handle_completion_report(context)
    # elif 'phase8-status' in msg_lower or 'phase8 status' in msg_lower or 'phase 8 status' in msg_lower:
    #     return handler.handle_phase8_status(context)
    # else:
    #     return f"Unknown Phase 8 operation: {message}"


def main():
    """Main CLI entry point with performance optimization."""
    start_time = time.perf_counter()
    
    parser = argparse.ArgumentParser(
        description="CORTEX AI Assistant - Natural Language Development Interface",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  cortex                              # Interactive mode
  cortex "help"                       # Show help
  cortex "create tests for auth.py"  # Single command
  cortex --setup                      # Run setup wizard
  cortex "status" --format json      # JSON output
  cortex --verbose "implement auth"  # Verbose logging
        """
    )
    
    parser.add_argument(
        "message",
        nargs="?",
        help="User message/command (omit for interactive mode)"
    )
    
    parser.add_argument(
        "--setup",
        action="store_true",
        help="Run CORTEX setup wizard"
    )
    
    parser.add_argument(
        "--repo",
        type=str,
        help="Repository path for setup (default: current directory)"
    )
    
    parser.add_argument(
        "--format",
        choices=["text", "json", "markdown"],
        default="text",
        help="Output format (default: text)"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    
    parser.add_argument(
        "--brain",
        type=str,
        help="Custom brain path (default: auto-detected)"
    )
    
    parser.add_argument(
        "--profile",
        action="store_true",
        help="Show performance profiling information"
    )
    
    # Phase 8: Final Integration & Cleanup arguments
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate operations without making changes (for integration-cleanup)"
    )
    
    parser.add_argument(
        "--operation-profile",
        choices=["quick", "standard", "comprehensive"],
        help="Cleanup profile: quick (cache/backups), standard (+old backups), comprehensive (+logs)"
    )
    
    parser.add_argument(
        "--output",
        type=str,
        help="Custom output path for reports"
    )
    
    args = parser.parse_args()
    
    # FAST PATH: Handle simple commands without full initialization
    if args.message and not args.setup and is_fast_command(args.message):
        try:
            handler = FastCommandHandler(brain_path=Path(args.brain) if args.brain else None)
            response = handler.handle(args.message, format_type=args.format)
            
            # Wrap response with CORTEX header/footer (AC-HEADER-001)
            wrapped_response = wrap_cortex_response(
                response,
                operation_type="Execution",
                format=args.format if args.format else "markdown",
                include_footer=True
            )
            
            print(wrapped_response)
            
            if args.profile:
                elapsed = (time.perf_counter() - start_time) * 1000
                print(f"\n⚡ Fast-path response time: {elapsed:.2f}ms")
            
            return 0
        except Exception as e:
            print(cortex_format(f"[ERROR] Fast-path handler failed: {e}", operation_type="Error", include_footer=False))
            # Fall through to full initialization
    
    # FULL PATH: Complex operations require full CortexEntry
    try:
        CortexEntry = _entry_module.CortexEntry
        entry = CortexEntry(
            brain_path=args.brain,
            enable_logging=args.verbose
        )
        
        if args.profile:
            init_time = (time.perf_counter() - start_time) * 1000
            print(f"⚙️ Initialization time: {init_time:.2f}ms")
    except Exception as e:
        print(cortex_format(f"[ERROR] Failed to initialize CORTEX: {e}", operation_type="Error", include_footer=False))
        return 1
    
    # Handle setup mode
    if args.setup:
        print("CORTEX Setup Wizard\n")
        results = entry.setup(repo_path=args.repo, verbose=True)
        
        if args.profile:
            elapsed = (time.perf_counter() - start_time) * 1000
            print(f"\n⚙️ Total time: {elapsed:.2f}ms")
        
        return 0 if results.get("success") else 1
    
    # Handle single command
    if args.message:
        try:
            command_start = time.perf_counter()
            
            # Check for fast utility commands (commit, align, healthcheck, optimize, deploy, system-maintenance, clear vscode)
            msg_lower = args.message.lower().strip()
            
            # Check for VS Code cache clearing
            if 'clear vscode' in msg_lower or 'clear vscode cache' in msg_lower or msg_lower in ['vscode-clear', 'vscode cache']:
                from src.tools.vscode_cache_cleaner import VSCodeCacheCleaner
                cleaner = VSCodeCacheCleaner()
                response = cleaner.report(dry_run=False)
            
            # Check for other utility commands
            elif msg_lower in ['commit', 'align', 'healthcheck', 'optimize', 'deploy', 'system-maintenance', 'system maintenance', 'maintenance']:
                # Normalize system maintenance commands
                command = msg_lower
                if command in ['system-maintenance', 'system maintenance', 'maintenance']:
                    command = 'system-maintenance'
                response = _handle_utility_command(command)
            # Check for Phase 8 operations
            elif _is_phase8_operation(args.message):
                response = _handle_phase8_operation(
                    args.message, 
                    entry, 
                    args
                )
            else:
                response = entry.process(
                    args.message,
                    resume_session=True,
                    format_type=args.format
                )
            
            # Wrap response with CORTEX header/footer (AC-HEADER-001)
            wrapped_response = wrap_cortex_response(
                response,
                operation_type="Execution",
                format=args.format if args.format else "markdown",
                include_footer=True
            )
            
            print(wrapped_response)
            
            if args.profile:
                command_time = (time.perf_counter() - command_start) * 1000
                total_time = (time.perf_counter() - start_time) * 1000
                print(f"\n⚙️ Command time: {command_time:.2f}ms")
                print(f"⚙️ Total time: {total_time:.2f}ms")
            
            return 0
        except Exception as e:
            print(f"[ERROR] {e}")
            return 1
    
    # Interactive mode
    print("CORTEX Interactive Mode")
    print("=" * 60)
    print("Enter your requests in natural language.")
    print("Type 'exit', 'quit', or press Ctrl+C to exit.")
    print("Type 'help' for available commands.")
    print("=" * 60)
    print()
    
    if args.profile:
        startup_time = (time.perf_counter() - start_time) * 1000
        print(f"⚙️ Startup time: {startup_time:.2f}ms\n")
    
    try:
        while True:
            try:
                user_input = input("You: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ["exit", "quit", "q"]:
                    print("\nGoodbye!")
                    break
                
                command_start = time.perf_counter()
                response = entry.process(
                    user_input,
                    resume_session=True,
                    format_type=args.format
                )
                
                # Wrap response with CORTEX header/footer (AC-HEADER-001)
                wrapped_response = wrap_cortex_response(
                    response,
                    operation_type="Execution",
                    format=args.format if args.format else "markdown",
                    include_footer=True
                )
                
                print(f"\n{wrapped_response}\n")
                
                if args.profile:
                    command_time = (time.perf_counter() - command_start) * 1000
                    print(f"⚙️ Response time: {command_time:.2f}ms\n")
                
            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                break
            except EOFError:
                print("\n\nGoodbye!")
                break
            except Exception as e:
                print(f"\n[ERROR] {e}\n")
                if args.verbose:
                    import traceback
                    traceback.print_exc()
    
    finally:
        # Cleanup
        entry.cleanup()
        
        if args.profile:
            # Show lazy loading stats
            from src.utils.lazy_loader import get_load_stats
            stats = get_load_stats()
            if stats['modules_loaded'] > 0:
                print("\n" + "="*60)
                print(f"📊 Loaded {stats['modules_loaded']} modules")
                print(f"⚡ Total load time: {stats['total_load_time']:.2f}ms")
                print(f"⚡ Average: {stats['avg_load_time']:.2f}ms")
                print("="*60)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
