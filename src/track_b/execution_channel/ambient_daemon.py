"""
CORTEX 3.0 Track B: Ambient Daemon
=================================

The Ambient Daemon is the central coordination component for Track B's execution channel.
It orchestrates file monitoring, git monitoring, and terminal tracking to capture
development context automatically without user intervention.

Key Features:
- Background process that runs continuously
- Coordinates multiple monitoring components
- Feeds captured data to Tier 1 memory system
- Handles macOS-specific optimizations
- Provides execution trace generation

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file for terms
"""

import asyncio
import logging
import signal
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from .file_monitor import FileMonitor
from .git_monitor import GitMonitor 
from .terminal_tracker import TerminalTracker


@dataclass
class DaemonConfig:
    """Configuration for the Ambient Daemon."""
    workspace_path: Path
    polling_interval: float = 1.0
    max_file_size: int = 1024 * 1024  # 1MB
    excluded_patterns: List[str] = None
    enable_git_hooks: bool = True
    enable_terminal_tracking: bool = True
    log_level: str = "INFO"
    
    def __post_init__(self):
        if self.excluded_patterns is None:
            self.excluded_patterns = [
                "*.pyc", "__pycache__", ".git", "node_modules",
                ".DS_Store", "*.log", ".cortex-temp"
            ]


@dataclass
class ExecutionEvent:
    """Represents a captured execution event."""
    timestamp: datetime
    event_type: str  # 'file_change', 'git_operation', 'terminal_command'
    source: str
    details: Dict[str, Any]
    context: Optional[Dict[str, Any]] = None


class AmbientDaemon:
    """
    Ambient Daemon for CORTEX Track B Execution Channel
    
    Continuously monitors development activity and feeds context
    to CORTEX brain without user intervention.
    """
    
    def __init__(self, config: DaemonConfig):
        self.config = config
        self.logger = self._setup_logging()
        self.is_running = False
        self.event_queue = asyncio.Queue()
        
        # Initialize monitoring components
        self.file_monitor = FileMonitor(
            workspace_path=config.workspace_path,
            excluded_patterns=config.excluded_patterns,
            max_file_size=config.max_file_size
        )
        
        self.git_monitor = GitMonitor(
            workspace_path=config.workspace_path,
            enable_hooks=config.enable_git_hooks
        ) if config.enable_git_hooks else None
        
        self.terminal_tracker = TerminalTracker(
            workspace_path=config.workspace_path
        ) if config.enable_terminal_tracking else None
        
        # Setup signal handlers for graceful shutdown
        self._setup_signal_handlers()
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for the daemon."""
        logger = logging.getLogger("cortex.track_b.ambient_daemon")
        logger.setLevel(getattr(logging, self.config.log_level))
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def _setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown."""
        def signal_handler(signum, frame):
            self.logger.info(f"Received signal {signum}, shutting down gracefully...")
            asyncio.create_task(self.stop())
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    async def start(self):
        """Start the ambient daemon."""
        if self.is_running:
            self.logger.warning("Daemon is already running")
            return
        
        self.logger.info("Starting CORTEX Track B Ambient Daemon")
        self.logger.info(f"Workspace: {self.config.workspace_path}")
        self.logger.info(f"Polling interval: {self.config.polling_interval}s")
        
        self.is_running = True
        
        # Start monitoring components
        await self._start_monitors()
        
        # Start main event loop
        await self._main_loop()
    
    async def stop(self):
        """Stop the ambient daemon gracefully."""
        if not self.is_running:
            return
        
        self.logger.info("Stopping ambient daemon...")
        self.is_running = False
        
        # Stop monitoring components
        await self._stop_monitors()
        
        self.logger.info("Ambient daemon stopped")
    
    async def _start_monitors(self):
        """Start all monitoring components."""
        try:
            # Start file monitor
            await self.file_monitor.start()
            self.logger.info("File monitor started")
            
            # Start git monitor if enabled
            if self.git_monitor:
                await self.git_monitor.start()
                self.logger.info("Git monitor started")
            
            # Start terminal tracker if enabled
            if self.terminal_tracker:
                await self.terminal_tracker.start()
                self.logger.info("Terminal tracker started")
                
        except Exception as e:
            self.logger.error(f"Failed to start monitors: {e}")
            raise
    
    async def _stop_monitors(self):
        """Stop all monitoring components."""
        try:
            if self.file_monitor:
                await self.file_monitor.stop()
                self.logger.debug("File monitor stopped")
            
            if self.git_monitor:
                await self.git_monitor.stop()
                self.logger.debug("Git monitor stopped")
            
            if self.terminal_tracker:
                await self.terminal_tracker.stop()
                self.logger.debug("Terminal tracker stopped")
                
        except Exception as e:
            self.logger.error(f"Error stopping monitors: {e}")
    
    async def _main_loop(self):
        """Main event processing loop."""
        self.logger.info("Starting main event loop")
        
        try:
            while self.is_running:
                # Collect events from monitors
                await self._collect_events()
                
                # Process events in queue
                await self._process_events()
                
                # Wait before next polling cycle
                await asyncio.sleep(self.config.polling_interval)
                
        except Exception as e:
            self.logger.error(f"Error in main loop: {e}")
            raise
    
    async def _collect_events(self):
        """Collect events from all monitoring components."""
        try:
            # Collect file events
            if self.file_monitor:
                file_events = await self.file_monitor.get_events()
                for event in file_events:
                    await self.event_queue.put(ExecutionEvent(
                        timestamp=datetime.now(),
                        event_type="file_change",
                        source="file_monitor",
                        details=event
                    ))
            
            # Collect git events  
            if self.git_monitor:
                git_events = await self.git_monitor.get_events()
                for event in git_events:
                    await self.event_queue.put(ExecutionEvent(
                        timestamp=datetime.now(),
                        event_type="git_operation",
                        source="git_monitor",
                        details=event
                    ))
            
            # Collect terminal events
            if self.terminal_tracker:
                terminal_events = await self.terminal_tracker.get_events()
                for event in terminal_events:
                    await self.event_queue.put(ExecutionEvent(
                        timestamp=datetime.now(),
                        event_type="terminal_command",
                        source="terminal_tracker",
                        details=event
                    ))
                    
        except Exception as e:
            self.logger.error(f"Error collecting events: {e}")
    
    async def _process_events(self):
        """Process events from the queue."""
        processed_count = 0
        
        try:
            # Process all queued events
            while not self.event_queue.empty():
                event = await self.event_queue.get()
                await self._handle_event(event)
                processed_count += 1
            
            if processed_count > 0:
                self.logger.debug(f"Processed {processed_count} events")
                
        except Exception as e:
            self.logger.error(f"Error processing events: {e}")
    
    async def _handle_event(self, event: ExecutionEvent):
        """Handle a single execution event."""
        try:
            # Log event for debugging
            self.logger.debug(f"Handling {event.event_type} from {event.source}")
            
            # TODO: Send event to Tier 1 memory system
            # This will be implemented when integrating with shared brain
            
            # For now, just log the event details
            self.logger.info(f"Event: {event.event_type} - {event.details.get('summary', 'No summary')}")
            
        except Exception as e:
            self.logger.error(f"Error handling event: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get current daemon status."""
        return {
            "is_running": self.is_running,
            "workspace": str(self.config.workspace_path),
            "components": {
                "file_monitor": self.file_monitor is not None and self.file_monitor.is_running if self.file_monitor else False,
                "git_monitor": self.git_monitor is not None and self.git_monitor.is_running if self.git_monitor else False,
                "terminal_tracker": self.terminal_tracker is not None and self.terminal_tracker.is_running if self.terminal_tracker else False,
            },
            "event_queue_size": self.event_queue.qsize(),
            "uptime": datetime.now() if self.is_running else None
        }


# CLI entry point for running the daemon standalone
async def main():
    """Main entry point for standalone daemon execution."""
    import argparse
    
    parser = argparse.ArgumentParser(description="CORTEX Track B Ambient Daemon")
    parser.add_argument("--workspace", type=Path, default=Path.cwd(),
                       help="Workspace path to monitor")
    parser.add_argument("--interval", type=float, default=1.0,
                       help="Polling interval in seconds")
    parser.add_argument("--log-level", default="INFO",
                       choices=["DEBUG", "INFO", "WARNING", "ERROR"],
                       help="Logging level")
    
    args = parser.parse_args()
    
    config = DaemonConfig(
        workspace_path=args.workspace,
        polling_interval=args.interval,
        log_level=args.log_level
    )
    
    daemon = AmbientDaemon(config)
    
    try:
        await daemon.start()
    except KeyboardInterrupt:
        await daemon.stop()
        sys.exit(0)
    except Exception as e:
        logging.error(f"Daemon failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())