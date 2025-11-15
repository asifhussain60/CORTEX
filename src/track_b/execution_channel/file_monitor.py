"""
CORTEX 3.0 Track B: File Monitor
===============================

File monitoring component for capturing filesystem changes in real-time.
Optimized for macOS with FSEvents integration and intelligent filtering.

Key Features:
- Real-time file system monitoring using FSEvents (macOS optimized)
- Intelligent filtering to avoid noise
- Content change detection and analysis
- Integration with CORTEX brain for context capture
- Performance optimized for large codebases

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file for terms
"""

import asyncio
import os
import hashlib
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass
import fnmatch

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler, FileSystemEvent
    WATCHDOG_AVAILABLE = True
except ImportError:
    # Fallback for environments without watchdog
    Observer = None
    FileSystemEventHandler = None
    FileSystemEvent = None
    WATCHDOG_AVAILABLE = False

# Import format converter for Track A/B compatibility
try:
    from ..integration.format_converter import create_universal_response
except ImportError:
    # Fallback if converter not available
    def create_universal_response(status: str, data: Any, **kwargs) -> Dict[str, Any]:
        return {"status": status, "result": data, "data": data, **kwargs}

# Type alias for optional use
if WATCHDOG_AVAILABLE:
    EventType = FileSystemEvent
else:
    from typing import Any
    EventType = Any


@dataclass
class FileChangeEvent:
    """Represents a file change event."""
    file_path: Path
    change_type: str  # 'created', 'modified', 'deleted', 'moved'
    timestamp: datetime
    file_size: int
    content_hash: Optional[str] = None
    diff_summary: Optional[str] = None
    

class FileMonitor:
    """
    File monitoring component for CORTEX Track B
    
    Monitors filesystem changes and provides intelligent filtering
    and content analysis for development context capture.
    """
    
    def __init__(self, workspace_path: Path, excluded_patterns: List[str], max_file_size: int):
        self.workspace_path = workspace_path
        self.excluded_patterns = excluded_patterns or []
        self.max_file_size = max_file_size
        self.logger = logging.getLogger("cortex.track_b.file_monitor")
        
        self.is_running = False
        self.observer = None
        self.event_handler = None
        self.event_queue = asyncio.Queue()
        
        # Cache for file hashes to detect content changes
        self.file_hashes: Dict[str, str] = {}
        
        # Recently processed files to avoid duplicate processing
        self.recent_files: Set[str] = set()
        
        self._validate_setup()
    
    def _validate_setup(self):
        """Validate the monitoring setup."""
        if not self.workspace_path.exists():
            raise ValueError(f"Workspace path does not exist: {self.workspace_path}")
        
        if not self.workspace_path.is_dir():
            raise ValueError(f"Workspace path is not a directory: {self.workspace_path}")
        
        if Observer is None:
            self.logger.warning("Watchdog not available, file monitoring will be limited")
    
    def _should_monitor_file(self, file_path: Path) -> bool:
        """Check if a file should be monitored based on exclusion patterns."""
        relative_path = file_path.relative_to(self.workspace_path)
        
        # Check against exclusion patterns
        for pattern in self.excluded_patterns:
            if fnmatch.fnmatch(str(relative_path), pattern) or fnmatch.fnmatch(file_path.name, pattern):
                return False
        
        # Skip if file is too large
        try:
            if file_path.is_file() and file_path.stat().st_size > self.max_file_size:
                self.logger.debug(f"Skipping large file: {relative_path}")
                return False
        except (OSError, PermissionError):
            return False
        
        # Skip hidden files unless they're important config files
        if file_path.name.startswith('.') and file_path.name not in ['.env', '.gitignore', '.cortex.config']:
            return False
        
        return True
    
    def _calculate_file_hash(self, file_path: Path) -> Optional[str]:
        """Calculate hash of file content for change detection."""
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
                return hashlib.md5(content).hexdigest()
        except (OSError, PermissionError, UnicodeDecodeError):
            return None
    
    def _get_change_type(self, event) -> str:
        """Determine the type of file system change."""
        if hasattr(event, 'event_type'):
            event_type_map = {
                'created': 'created',
                'modified': 'modified', 
                'deleted': 'deleted',
                'moved': 'moved'
            }
            return event_type_map.get(event.event_type, 'modified')
        return 'modified'
    
    async def start(self):
        """Start file monitoring."""
        if self.is_running:
            self.logger.warning("File monitor is already running")
            return
        
        self.logger.info(f"Starting file monitor for: {self.workspace_path}")
        
        if Observer is None:
            self.logger.warning("File monitoring disabled: watchdog not available")
            return
        
        # Create event handler
        self.event_handler = FileSystemEventHandler()
        self.event_handler.on_any_event = self._on_file_event
        
        # Setup observer
        self.observer = Observer()
        self.observer.schedule(
            self.event_handler, 
            str(self.workspace_path), 
            recursive=True
        )
        
        # Start monitoring
        self.observer.start()
        self.is_running = True
        
        self.logger.info("File monitor started successfully")
    
    async def stop(self):
        """Stop file monitoring."""
        if not self.is_running:
            return
        
        self.logger.info("Stopping file monitor...")
        
        if self.observer:
            self.observer.stop()
            self.observer.join()
        
        self.is_running = False
        self.logger.info("File monitor stopped")
    
    def _on_file_event(self, event):
        """Handle file system events."""
        try:
            if event.is_directory:
                return
            
            file_path = Path(event.src_path)
            
            # Check if we should monitor this file
            if not self._should_monitor_file(file_path):
                return
            
            # Avoid processing the same file multiple times rapidly
            file_key = str(file_path)
            if file_key in self.recent_files:
                return
            
            self.recent_files.add(file_key)
            
            # Process the file change - use thread-safe method
            try:
                loop = asyncio.get_event_loop()
                if loop and loop.is_running():
                    asyncio.create_task(self._process_file_change(file_path, event))
                else:
                    # If no event loop is running, we'll queue it for later
                    asyncio.ensure_future(self._process_file_change(file_path, event))
            except RuntimeError:
                # No event loop available, skip for now
                pass
            
            # Clean up recent files set periodically
            if len(self.recent_files) > 1000:
                self.recent_files.clear()
                
        except Exception as e:
            self.logger.error(f"Error handling file event: {e}")
    
    async def _process_file_change(self, file_path: Path, event):
        """Process a file change event with enhanced intelligence."""
        try:
            change_type = self._get_change_type(event)
            timestamp = datetime.now()
            
            # Calculate file info
            file_size = 0
            content_hash = None
            
            if file_path.exists() and file_path.is_file():
                try:
                    file_size = file_path.stat().st_size
                    content_hash = self._calculate_file_hash(file_path)
                except (OSError, PermissionError):
                    pass
            
            # Check if content actually changed
            file_key = str(file_path)
            old_hash = self.file_hashes.get(file_key)
            
            if change_type == 'modified' and content_hash == old_hash:
                # Content didn't actually change, skip
                return
            
            # Enhanced Intelligence: Analyze content changes
            content_analysis = await self._analyze_content_changes(file_path, change_type)
            
            # Update hash cache
            if content_hash:
                self.file_hashes[file_key] = content_hash
            elif change_type == 'deleted':
                self.file_hashes.pop(file_key, None)
            
            # Create file change event
            change_event = FileChangeEvent(
                file_path=file_path,
                change_type=change_type,
                timestamp=timestamp,
                file_size=file_size,
                content_hash=content_hash,
                diff_summary=await self._generate_diff_summary(file_path, change_type)
            )
            
            # Queue the event for processing
            await self.event_queue.put(change_event)
            
            self.logger.debug(f"Processed file change: {change_type} - {file_path.name}")
            
        except Exception as e:
            self.logger.error(f"Error processing file change: {e}")
        finally:
            # Remove from recent files after processing
            self.recent_files.discard(str(file_path))
    
    async def _generate_diff_summary(self, file_path: Path, change_type: str) -> Optional[str]:
        """Generate a summary of file changes."""
        try:
            if change_type == 'deleted':
                return f"File deleted: {file_path.name}"
            elif change_type == 'created':
                if file_path.suffix in ['.py', '.js', '.ts', '.java', '.cpp', '.c', '.go', '.rs']:
                    return f"New {file_path.suffix[1:].upper()} file: {file_path.name}"
                else:
                    return f"New file: {file_path.name}"
            elif change_type == 'modified':
                # For text files, we could analyze the diff
                if file_path.suffix in ['.py', '.js', '.ts', '.md', '.txt', '.json', '.yaml', '.yml']:
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            lines = content.count('\n') + 1
                            chars = len(content)
                            return f"Modified {file_path.name}: {lines} lines, {chars} chars"
                    except (OSError, UnicodeDecodeError):
                        pass
                
                return f"Modified: {file_path.name}"
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error generating diff summary: {e}")
            return None
    
    async def _analyze_content_changes(self, file_path: Path, change_type: str) -> Dict[str, Any]:
        """Enhanced Intelligence: Analyze content changes for semantic understanding."""
        analysis = {
            'file_type': self._detect_file_type(file_path),
            'complexity_score': 0,
            'semantic_changes': [],
            'potential_impact': 'low',
            'recommendations': []
        }
        
        try:
            if not file_path.exists() or file_path.stat().st_size > self.max_file_size:
                return analysis
            
            # Read file content for analysis
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            lines = content.split('\n')
            
            # Analyze file type and content
            analysis['line_count'] = len(lines)
            analysis['complexity_score'] = self._calculate_complexity_score(content, file_path.suffix)
            
            # Detect semantic changes based on file type
            if file_path.suffix in ['.py', '.js', '.ts', '.java', '.cpp', '.c']:
                analysis['semantic_changes'] = self._analyze_code_changes(content, file_path)
            elif file_path.suffix in ['.md', '.txt', '.rst']:
                analysis['semantic_changes'] = self._analyze_documentation_changes(content, file_path)
            elif file_path.suffix in ['.json', '.yaml', '.yml', '.xml']:
                analysis['semantic_changes'] = self._analyze_config_changes(content, file_path)
            
            # Assess potential impact
            analysis['potential_impact'] = self._assess_impact_level(analysis, file_path)
            
            # Generate recommendations
            analysis['recommendations'] = self._generate_recommendations(analysis, file_path)
            
            self.logger.debug(f"Content analysis for {file_path.name}: {analysis['potential_impact']} impact")
            
        except Exception as e:
            self.logger.error(f"Error analyzing content changes for {file_path}: {e}")
        
        return analysis
    
    def _detect_file_type(self, file_path: Path) -> str:
        """Detect the type of file for appropriate analysis."""
        suffix = file_path.suffix.lower()
        
        if suffix in ['.py']:
            return 'python_code'
        elif suffix in ['.js', '.ts']:
            return 'javascript_code'
        elif suffix in ['.java']:
            return 'java_code'
        elif suffix in ['.cpp', '.c', '.h']:
            return 'c_cpp_code'
        elif suffix in ['.md', '.rst']:
            return 'documentation'
        elif suffix in ['.json', '.yaml', '.yml']:
            return 'configuration'
        elif suffix in ['.html', '.css']:
            return 'web_frontend'
        elif suffix in ['.sql']:
            return 'database'
        else:
            return 'generic_text'
    
    def _calculate_complexity_score(self, content: str, file_suffix: str) -> int:
        """Calculate a complexity score for the file content."""
        lines = content.split('\n')
        non_empty_lines = [line for line in lines if line.strip()]
        
        # Basic complexity metrics
        complexity = len(non_empty_lines)
        
        if file_suffix in ['.py', '.js', '.ts', '.java']:
            # Code-specific complexity
            complexity += content.count('def ') * 2  # Functions
            complexity += content.count('class ') * 3  # Classes
            complexity += content.count('if ') + content.count('while ') + content.count('for ')  # Control flow
            complexity += content.count('import ') + content.count('from ')  # Dependencies
        
        return min(complexity, 1000)  # Cap at 1000
    
    def _analyze_code_changes(self, content: str, file_path: Path) -> List[str]:
        """Analyze semantic changes in code files."""
        changes = []
        
        # Function definitions
        function_count = content.count('def ') + content.count('function ')
        if function_count > 0:
            changes.append(f"functions_detected: {function_count}")
        
        # Class definitions
        class_count = content.count('class ')
        if class_count > 0:
            changes.append(f"classes_detected: {class_count}")
        
        # Import statements
        import_count = content.count('import ') + content.count('from ')
        if import_count > 0:
            changes.append(f"imports_detected: {import_count}")
        
        # Test-related content
        if any(test_keyword in content.lower() for test_keyword in ['test_', 'def test', 'it(', 'describe(']):
            changes.append("test_code_detected")
        
        # Error handling
        if any(error_keyword in content for error_keyword in ['try:', 'except:', 'catch(', 'throw ']):
            changes.append("error_handling_detected")
        
        return changes
    
    def _analyze_documentation_changes(self, content: str, file_path: Path) -> List[str]:
        """Analyze semantic changes in documentation files."""
        changes = []
        
        lines = content.split('\n')
        
        # Headers
        header_count = sum(1 for line in lines if line.strip().startswith('#'))
        if header_count > 0:
            changes.append(f"headers_detected: {header_count}")
        
        # Code blocks
        code_block_count = content.count('```')
        if code_block_count > 0:
            changes.append(f"code_blocks_detected: {code_block_count // 2}")
        
        # Links
        link_count = content.count('[') + content.count('](')
        if link_count > 0:
            changes.append(f"links_detected: {link_count}")
        
        return changes
    
    def _analyze_config_changes(self, content: str, file_path: Path) -> List[str]:
        """Analyze semantic changes in configuration files."""
        changes = []
        
        try:
            if file_path.suffix.lower() == '.json':
                data = json.loads(content)
                changes.append(f"json_keys: {len(data) if isinstance(data, dict) else 'array'}")
            elif file_path.suffix.lower() in ['.yml', '.yaml']:
                # Basic YAML analysis without importing yaml
                lines = [line for line in content.split('\n') if line.strip() and not line.strip().startswith('#')]
                root_keys = sum(1 for line in lines if not line.startswith(' ') and ':' in line)
                changes.append(f"yaml_root_keys: {root_keys}")
        except Exception:
            changes.append("config_parsing_error")
        
        return changes
    
    def _assess_impact_level(self, analysis: Dict[str, Any], file_path: Path) -> str:
        """Assess the potential impact level of file changes."""
        
        # High impact indicators
        if any(change.startswith('classes_detected') for change in analysis['semantic_changes']):
            return 'high'
        
        if analysis['complexity_score'] > 500:
            return 'high'
        
        if 'test_code_detected' in analysis['semantic_changes']:
            return 'medium'
        
        if file_path.name in ['requirements.txt', 'package.json', 'Dockerfile', 'docker-compose.yml']:
            return 'high'
        
        if file_path.suffix in ['.yaml', '.yml', '.json'] and 'config' in file_path.name.lower():
            return 'medium'
        
        # Default to low impact
        return 'low'
    
    def _generate_recommendations(self, analysis: Dict[str, Any], file_path: Path) -> List[str]:
        """Generate intelligent recommendations based on file analysis."""
        recommendations = []
        
        if analysis['potential_impact'] == 'high':
            recommendations.append("Consider running tests after this change")
            recommendations.append("Review for potential breaking changes")
        
        if analysis['complexity_score'] > 300:
            recommendations.append("Consider refactoring for maintainability")
        
        if 'error_handling_detected' in analysis['semantic_changes']:
            recommendations.append("Verify error handling edge cases")
        
        if analysis['file_type'] == 'configuration':
            recommendations.append("Validate configuration syntax")
            recommendations.append("Check for security implications")
        
        if 'test_code_detected' in analysis['semantic_changes']:
            recommendations.append("Run test suite to verify functionality")
        
        return recommendations
    
    async def get_events(self) -> List[Dict[str, Any]]:
        """Get all pending file change events."""
        events = []
        
        try:
            # Collect all queued events
            while not self.event_queue.empty():
                event = await self.event_queue.get()
                events.append({
                    'type': 'file_change',
                    'file_path': str(event.file_path),
                    'relative_path': str(event.file_path.relative_to(self.workspace_path)),
                    'change_type': event.change_type,
                    'timestamp': event.timestamp.isoformat(),
                    'file_size': event.file_size,
                    'content_hash': event.content_hash,
                    'diff_summary': event.diff_summary,
                    'summary': f"{event.change_type.capitalize()}: {event.file_path.name}"
                })
        except Exception as e:
            self.logger.error(f"Error getting events: {e}")
        
        return events
    
    def get_status(self) -> Dict[str, Any]:
        """Get file monitor status."""
        return {
            'is_running': self.is_running,
            'workspace_path': str(self.workspace_path),
            'excluded_patterns': self.excluded_patterns,
            'max_file_size': self.max_file_size,
            'tracked_files': len(self.file_hashes),
            'pending_events': self.event_queue.qsize(),
            'watchdog_available': Observer is not None
        }

    def get_health(self) -> Dict[str, Any]:
        """Get health status for component interface compliance."""
        errors = []
        
        # Check workspace accessibility
        if not self.workspace_path.exists():
            errors.append("Workspace path does not exist")
        elif not self.workspace_path.is_dir():
            errors.append("Workspace path is not a directory")
        
        # Check watchdog availability
        if not Observer:
            errors.append("Watchdog library not available")
        
        # Check if running state is consistent
        if self.is_running and Observer and hasattr(self, 'observer') and not self.observer.is_alive():
            errors.append("Observer process not running despite is_running=True")
        
        health_status = "healthy" if len(errors) == 0 else "unhealthy"
        
        return {
            "overall_health": health_status,
            "errors": errors,
            "metrics": {
                "tracked_files": len(self.file_hashes),
                "pending_events": self.event_queue.qsize(),
                "is_running": self.is_running
            },
            "timestamp": datetime.now().isoformat()
        }

    def initialize(self) -> bool:
        """Initialize the file monitor for operation interface compliance."""
        try:
            # Initialization is handled in __init__, just validate setup
            if not self.workspace_path.exists():
                self.logger.error(f"Workspace path does not exist: {self.workspace_path}")
                return False
                
            if not Observer:
                self.logger.warning("Watchdog not available, file monitoring will be limited")
                
            self.logger.info("File monitor initialized successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize file monitor: {e}")
            return False

    async def execute(self, request: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute file monitor operation for operation interface compliance."""
        if context is None:
            context = {}
            
        self.logger.debug(f"Executing request: {request}")
        
        try:
            if request == "start":
                await self.start()
                return create_universal_response("success", {"message": "File monitor started successfully"})
            elif request == "stop":
                await self.stop()
                return create_universal_response("success", {"message": "File monitor stopped successfully"})
            elif request == "status":
                status = self.get_status()
                return create_universal_response("success", status)
            elif request == "health":
                health = self.get_health()
                return create_universal_response("success", health)
            elif request == "get_events":
                events = await self.get_events()
                return create_universal_response("success", {"events": events})
            else:
                return create_universal_response("error", {"message": f"Unknown request: {request}"})
        except Exception as e:
            self.logger.error(f"Failed to execute request {request}: {e}")
            return create_universal_response("error", {"message": str(e)})

    def cleanup(self) -> bool:
        """Cleanup file monitor resources for operation interface compliance."""
        try:
            self.logger.info("Cleaning up file monitor resources")
            
            # Stop monitoring if running
            if self.is_running:
                asyncio.create_task(self.stop())
            
            # Clear file hashes
            self.file_hashes.clear()
            
            # Clear event queue
            while not self.event_queue.empty():
                try:
                    self.event_queue.get_nowait()
                except:
                    break
                    
            return True
        except Exception as e:
            self.logger.error(f"Failed to cleanup file monitor: {e}")
            return False