"""
Workspace Topology Crawler for CORTEX

Fast structural analysis of multi-application workspaces.
Detects application boundaries, shared code, and technology signatures.

Target: <5 seconds for 100+ folders

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import os
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass

from .base_crawler import BaseCrawler, CrawlerResult, CrawlerStatus, CrawlerPriority

logger = logging.getLogger(__name__)


@dataclass
class ApplicationInfo:
    """Information about discovered application"""
    name: str
    path: str
    marker: str
    estimated_size: int
    estimated_file_count: int
    technology_stack: List[str]
    last_modified: datetime
    has_tests: bool
    has_database_access: bool


class WorkspaceTopologyCrawler(BaseCrawler):
    """
    Fast structural analysis of multi-application workspaces.
    
    Detects:
    - Application boundaries (folders with specific markers)
    - Shared code locations (Common/, CommonCFCs/, etc.)
    - Technology signatures (ColdFusion, Java, JavaScript, etc.)
    - Database access patterns
    
    Execution Time: <5 seconds for 100+ folders
    Memory Usage: <50MB
    """
    
    # Application detection markers (priority order)
    APPLICATION_MARKERS = [
        'Application.cfc',      # ColdFusion application
        'Application.cfm',      # ColdFusion legacy
        'index.cfm',           # ColdFusion entry point
        'package.json',        # Node.js application
        'pom.xml',             # Java/Maven application
        'build.gradle',        # Java/Gradle application
        'index.html',          # Static web application
        'app.py',              # Python Flask/Django
        'manage.py',           # Django application
        'requirements.txt',    # Python application
        'composer.json',       # PHP application
        'web.config',          # ASP.NET application
    ]
    
    # Shared code folder patterns
    SHARED_CODE_PATTERNS = [
        'Common',
        'CommonCFCs',
        'Shared',
        'Lib',
        'Libraries',
        'Utils',
        'Utilities',
        'Core',
    ]
    
    # Database access indicators
    DATABASE_INDICATORS = [
        'datasource',
        'cfquery',
        'jdbc',
        'orm',
        'hibernate',
        'entity',
    ]
    
    def get_crawler_info(self) -> Dict[str, Any]:
        """Get crawler metadata"""
        return {
            'crawler_id': 'workspace_topology',
            'name': 'Workspace Topology Crawler',
            'description': 'Fast multi-application workspace structure detection',
            'version': '1.0.0',
            'priority': CrawlerPriority.CRITICAL,
            'dependencies': [],
            'estimated_time_seconds': 5,
            'scope': 'workspace'
        }
    
    def execute(self) -> CrawlerResult:
        """Execute workspace topology detection"""
        start_time = datetime.now()
        
        try:
            logger.info(f"Starting workspace topology analysis: {self.workspace_path}")
            
            # Detect workspace type
            workspace_type = self._detect_workspace_type()
            
            # Discover applications
            applications = self._discover_applications()
            
            # Find shared code
            shared_libraries = self._find_shared_code()
            
            # Quick file count estimate
            total_estimated_files = sum(app.estimated_file_count for app in applications)
            
            # Build topology structure
            topology = {
                'workspace_type': workspace_type,
                'workspace_path': str(self.workspace_path),
                'total_applications': len(applications),
                'applications': [self._app_to_dict(app) for app in applications],
                'shared_libraries': shared_libraries,
                'total_estimated_files': total_estimated_files,
                'analysis_timestamp': datetime.now().isoformat(),
                'analysis_duration_seconds': (datetime.now() - start_time).total_seconds()
            }
            
            # Store in Knowledge Graph
            if self.knowledge_graph:
                self.knowledge_graph.add_pattern(
                    scope='workspace',
                    namespace='topology',
                    pattern_type='structure',
                    data=topology,
                    confidence=0.95,
                    tags=['multi-application', 'workspace-structure']
                )
                logger.info("Stored workspace topology in Knowledge Graph")
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            logger.info(f"Workspace topology analysis complete: {len(applications)} apps in {duration:.2f}s")
            
            return CrawlerResult(
                crawler_id=self.get_crawler_info()['crawler_id'],
                crawler_name='WorkspaceTopology',
                status=CrawlerStatus.COMPLETED,
                started_at=start_time,
                completed_at=end_time,
                duration_seconds=duration,
                items_discovered=len(applications),
                patterns_created=1,
                metadata={
                    'workspace_type': workspace_type,
                    'total_applications': len(applications),
                    'shared_libraries': len(shared_libraries),
                    'estimated_files': total_estimated_files,
                    'topology_data': topology
                }
            )
            
        except Exception as e:
            logger.error(f"Workspace topology analysis failed: {e}", exc_info=True)
            end_time = datetime.now()
            return CrawlerResult(
                crawler_id=self.get_crawler_info()['crawler_id'],
                crawler_name='WorkspaceTopology',
                status=CrawlerStatus.FAILED,
                started_at=start_time,
                completed_at=end_time,
                duration_seconds=(end_time - start_time).total_seconds(),
                items_discovered=0,
                errors=[str(e)]
            )
    
    def _detect_workspace_type(self) -> str:
        """
        Detect workspace type based on structure.
        
        Types:
        - multi-application: Multiple independent applications
        - monorepo: Single repository with multiple packages
        - microservices: Service-oriented architecture
        - monolithic: Single large application
        """
        # Count potential applications at root level
        app_count = 0
        for entry in os.scandir(self.workspace_path):
            if entry.is_dir() and not entry.name.startswith('.'):
                for marker in self.APPLICATION_MARKERS:
                    if (Path(entry.path) / marker).exists():
                        app_count += 1
                        break
        
        if app_count >= 5:
            return 'multi-application'
        elif app_count >= 2:
            return 'monorepo'
        elif (self.workspace_path / 'services').exists() or (self.workspace_path / 'microservices').exists():
            return 'microservices'
        else:
            return 'monolithic'
    
    def _discover_applications(self) -> List[ApplicationInfo]:
        """
        Fast discovery of applications using os.scandir.
        
        Optimizations:
        - Uses os.scandir (faster than glob)
        - Stops at first marker match (no exhaustive search)
        - Estimates size without full traversal
        """
        applications = []
        
        for entry in os.scandir(self.workspace_path):
            # Skip hidden folders and common non-app folders
            if not entry.is_dir() or entry.name.startswith('.'):
                continue
            
            if entry.name in ['node_modules', 'vendor', '__pycache__', 'venv', '.git']:
                continue
            
            # Check for application markers
            app_path = Path(entry.path)
            for marker in self.APPLICATION_MARKERS:
                marker_path = app_path / marker
                if marker_path.exists():
                    # Found an application
                    app_info = ApplicationInfo(
                        name=entry.name,
                        path=str(app_path),
                        marker=marker,
                        estimated_size=self._estimate_size(app_path),
                        estimated_file_count=self._estimate_file_count(app_path),
                        technology_stack=self._detect_tech_stack(app_path),
                        last_modified=datetime.fromtimestamp(entry.stat().st_mtime),
                        has_tests=self._has_tests(app_path),
                        has_database_access=self._has_database_access(app_path)
                    )
                    applications.append(app_info)
                    break  # Stop at first marker
        
        # Sort by name for consistent ordering
        applications.sort(key=lambda x: x.name)
        
        logger.info(f"Discovered {len(applications)} applications")
        return applications
    
    def _estimate_size(self, app_path: Path) -> int:
        """
        Quick size estimate without full traversal.
        
        Uses sampling: checks first 100 files and extrapolates.
        """
        sample_size = 0
        sample_count = 0
        max_samples = 100
        
        try:
            for root, dirs, files in os.walk(app_path):
                # Skip common large folders
                dirs[:] = [d for d in dirs if d not in 
                          ['.git', 'node_modules', 'vendor', '__pycache__', 'venv', 'bin', 'obj']]
                
                for file in files[:max_samples - sample_count]:
                    try:
                        file_path = Path(root) / file
                        sample_size += file_path.stat().st_size
                        sample_count += 1
                    except (OSError, PermissionError):
                        pass
                
                if sample_count >= max_samples:
                    break
            
            # Extrapolate total size
            if sample_count > 0:
                estimated_total_files = self._estimate_file_count(app_path)
                avg_file_size = sample_size / sample_count
                return int(avg_file_size * estimated_total_files)
        except Exception as e:
            logger.warning(f"Size estimation failed for {app_path}: {e}")
        
        return 0
    
    def _estimate_file_count(self, app_path: Path) -> int:
        """
        Estimate total file count without full traversal.
        
        Uses sampling: counts files in first 10 directories.
        """
        sample_count = 0
        dir_count = 0
        max_dirs = 10
        
        try:
            for root, dirs, files in os.walk(app_path):
                # Skip common large folders
                dirs[:] = [d for d in dirs if d not in 
                          ['.git', 'node_modules', 'vendor', '__pycache__', 'venv']]
                
                sample_count += len(files)
                dir_count += 1
                
                if dir_count >= max_dirs:
                    break
            
            # Extrapolate (rough estimate)
            if dir_count > 0:
                return int((sample_count / dir_count) * dir_count * 5)  # Assume 5x more dirs
        except Exception:
            pass
        
        return 100  # Default estimate
    
    def _detect_tech_stack(self, app_path: Path) -> List[str]:
        """
        Detect technology stack from file patterns.
        
        Fast detection using file existence checks only.
        """
        tech_stack = []
        
        # ColdFusion
        if (app_path / 'Application.cfc').exists() or (app_path / 'Application.cfm').exists():
            tech_stack.append('ColdFusion')
        
        # Java
        if (app_path / 'pom.xml').exists() or (app_path / 'build.gradle').exists():
            tech_stack.append('Java')
        
        # JavaScript/Node.js
        if (app_path / 'package.json').exists():
            tech_stack.append('JavaScript/Node.js')
        
        # Python
        if (app_path / 'requirements.txt').exists() or (app_path / 'setup.py').exists():
            tech_stack.append('Python')
        
        # .NET
        if (app_path / 'web.config').exists() or list(app_path.glob('*.csproj')):
            tech_stack.append('.NET')
        
        # PHP
        if (app_path / 'composer.json').exists():
            tech_stack.append('PHP')
        
        return tech_stack if tech_stack else ['Unknown']
    
    def _has_tests(self, app_path: Path) -> bool:
        """Check if application has test directory"""
        test_dirs = ['tests', 'test', 'spec', '__tests__', 'Test']
        return any((app_path / test_dir).exists() for test_dir in test_dirs)
    
    def _has_database_access(self, app_path: Path) -> bool:
        """
        Check if application has database access patterns.
        
        Fast check using file content sampling.
        """
        # Check for database configuration files
        db_config_files = [
            'datasource.cfm',
            'database.yml',
            'hibernate.cfg.xml',
            'application.properties',
            'appsettings.json'
        ]
        
        for config_file in db_config_files:
            if (app_path / config_file).exists():
                return True
        
        # Sample check: look for database keywords in first few CF files
        try:
            cf_files = list(app_path.glob('*.cfm'))[:5]
            for cf_file in cf_files:
                try:
                    content = cf_file.read_text(encoding='utf-8', errors='ignore')[:5000]  # First 5KB
                    if any(indicator in content.lower() for indicator in self.DATABASE_INDICATORS):
                        return True
                except Exception:
                    pass
        except Exception:
            pass
        
        return False
    
    def _find_shared_code(self) -> List[Dict[str, str]]:
        """
        Find shared code libraries across applications.
        
        Returns list of shared library locations.
        """
        shared_libs = []
        
        for entry in os.scandir(self.workspace_path):
            if not entry.is_dir() or entry.name.startswith('.'):
                continue
            
            # Check if folder name matches shared code patterns
            if entry.name in self.SHARED_CODE_PATTERNS:
                shared_libs.append({
                    'name': entry.name,
                    'path': entry.path,
                    'type': 'shared_library'
                })
        
        logger.info(f"Found {len(shared_libs)} shared libraries")
        return shared_libs
    
    def _app_to_dict(self, app: ApplicationInfo) -> Dict[str, Any]:
        """Convert ApplicationInfo to dictionary"""
        return {
            'name': app.name,
            'path': app.path,
            'marker': app.marker,
            'estimated_size': app.estimated_size,
            'estimated_file_count': app.estimated_file_count,
            'technology_stack': app.technology_stack,
            'last_modified': app.last_modified.isoformat(),
            'has_tests': app.has_tests,
            'has_database_access': app.has_database_access
        }
    
    def crawl(self) -> CrawlerResult:
        """
        Execute workspace topology analysis.
        
        Returns:
            CrawlerResult with discovered applications and topology
        """
        start_time = datetime.now()
        
        try:
            # Discover applications
            applications = self._discover_applications()
            
            # Find shared code
            shared_libs = self._find_shared_code()
            
            # Detect workspace type
            workspace_type = self._detect_workspace_type(applications)
            
            # Build topology data
            data = {
                'workspace_type': workspace_type,
                'applications': [self._app_to_dict(app) for app in applications],
                'shared_libraries': shared_libs,
                'total_applications': len(applications),
                'total_shared_libraries': len(shared_libs)
            }
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            return CrawlerResult(
                crawler_id=f"workspace_topology_{start_time.strftime('%Y%m%d_%H%M%S')}",
                crawler_name='WorkspaceTopology',
                status=CrawlerStatus.COMPLETED,
                started_at=start_time,
                completed_at=end_time,
                duration_seconds=duration,
                items_discovered=len(applications) + len(shared_libs),
                metadata={
                    'workspace_path': str(self.workspace_path),
                    'workspace_type': workspace_type,
                    'topology_data': data
                }
            )
        
        except Exception as e:
            logger.error(f"Workspace topology crawl failed: {e}")
            end_time = datetime.now()
            return CrawlerResult(
                crawler_id=f"workspace_topology_{start_time.strftime('%Y%m%d_%H%M%S')}",
                crawler_name='WorkspaceTopology',
                status=CrawlerStatus.FAILED,
                started_at=start_time,
                completed_at=end_time,
                duration_seconds=(end_time - start_time).total_seconds(),
                errors=[str(e)]
            )
    
    def validate(self) -> bool:
        """
        Validate workspace path exists and is accessible.
        
        Returns:
            True if workspace is valid, False otherwise
        """
        try:
            return self.workspace_path.exists() and self.workspace_path.is_dir()
        except Exception as e:
            logger.error(f"Workspace validation failed: {e}")
            return False
    
    def store_results(self, result: CrawlerResult) -> None:
        """
        Store topology results to knowledge graph.
        
        Args:
            result: CrawlerResult to store
        """
        if not self.knowledge_graph or result.status != CrawlerStatus.COMPLETED:
            return
        
        try:
            # Extract topology data from metadata
            topology_data = result.metadata.get('topology_data', {})
            
            # Store workspace topology metadata
            self.knowledge_graph.add_node(
                node_type='workspace_topology',
                node_id=f"topology_{result.started_at.strftime('%Y%m%d_%H%M%S')}",
                data={
                    'workspace_type': result.metadata.get('workspace_type'),
                    'total_applications': topology_data.get('total_applications'),
                    'total_shared_libraries': topology_data.get('total_shared_libraries'),
                    'analyzed_at': result.completed_at.isoformat() if result.completed_at else None,
                    'duration_seconds': result.duration_seconds
                }
            )
            
            # Store application nodes
            for app in topology_data.get('applications', []):
                self.knowledge_graph.add_node(
                    node_type='application',
                    node_id=app['name'],
                    data=app
                )
            
            # Store shared library nodes
            for lib in topology_data.get('shared_libraries', []):
                self.knowledge_graph.add_node(
                    node_type='shared_library',
                    node_id=lib['name'],
                    data=lib
                )
            
            logger.info(f"Stored topology results for {topology_data.get('total_applications')} applications")
        
        except Exception as e:
            logger.error(f"Failed to store topology results: {e}")
