"""
Application-Scoped Crawler for CORTEX

Crawls a single application with shallow/deep modes and intelligent caching.

Target: <10 seconds for shallow crawl

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import os
import json
import hashlib
import subprocess
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass

from .base_crawler import BaseCrawler, CrawlerResult, CrawlerStatus, CrawlerPriority

logger = logging.getLogger(__name__)


@dataclass
class ApplicationContext:
    """Context information for an application"""
    app_name: str
    entry_points: List[Dict[str, Any]]
    structure: Dict[str, Any]
    configuration: Dict[str, Any]
    file_inventory: Optional[List[Dict[str, Any]]] = None
    relationships: Optional[List[Dict[str, Any]]] = None
    database_references: Optional[List[Dict[str, Any]]] = None


class ApplicationScopedCrawler(BaseCrawler):
    """
    Crawls a single application in isolation.
    
    Features:
    - Application boundary awareness
    - Shallow vs deep crawl modes
    - Fingerprint-based caching
    - Skip if unchanged (git hash based)
    
    Modes:
    - shallow: Entry points + structure + config (target: <10s)
    - deep: Full file inventory + relationships + DB refs (target: <60s)
    """
    
    ENTRY_POINT_PATTERNS = [
        'index.cfm',
        'Application.cfc',
        'Application.cfm',
        'index.html',
        'index.js',
        'main.py',
        'app.py',
        'server.js',
        'index.php',
    ]
    
    CONFIGURATION_FILES = [
        'Application.cfc',
        'Application.cfm',
        'web.config',
        'package.json',
        'pom.xml',
        'build.gradle',
        'requirements.txt',
        'composer.json',
        'appsettings.json',
        'hibernate.cfg.xml',
    ]
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize application-scoped crawler.
        
        Args:
            config: Configuration dictionary with:
                - workspace_path: Path to workspace root
                - application_name: Name of application to crawl
                - depth: 'shallow' or 'deep'
                - knowledge_graph: Optional KnowledgeGraph instance
                - cache_manager: Optional cache manager instance
        """
        super().__init__(config)
        self.app_name = config.get('application_name')
        self.depth = config.get('depth', 'shallow')
        self.cache_manager = config.get('cache_manager')
        
        if not self.app_name:
            raise ValueError("application_name is required")
        
        self.app_path = Path(self.workspace_path) / self.app_name
        
        if not self.app_path.exists():
            raise ValueError(f"Application path does not exist: {self.app_path}")
    
    def get_crawler_info(self) -> Dict[str, Any]:
        """Get crawler metadata"""
        return {
            'crawler_id': f'application_scoped_{self.app_name}',
            'name': f'Application Crawler: {self.app_name}',
            'description': f'Crawl {self.app_name} application ({self.depth} mode)',
            'version': '1.0.0',
            'priority': CrawlerPriority.HIGH,
            'dependencies': ['workspace_topology'],
            'estimated_time_seconds': 10 if self.depth == 'shallow' else 60,
            'scope': 'application'
        }
    
    def execute(self) -> CrawlerResult:
        """Execute application crawl with caching"""
        start_time = datetime.now()
        
        try:
            logger.info(f"Starting {self.depth} crawl for {self.app_name}")
            
            # Generate cache key (fingerprint)
            fingerprint = self._generate_fingerprint()
            
            # Check cache first
            if self.cache_manager:
                cached = self.cache_manager.get(self.app_name, self.depth, fingerprint)
                if cached:
                    logger.info(f"Using cached context for {self.app_name}")
                    return CrawlerResult(
                        crawler_id=self.get_crawler_info()['crawler_id'],
                        status=CrawlerStatus.COMPLETED,
                        items_discovered=cached.get('item_count', 0),
                        patterns_created=0,  # Used cached
                        execution_time=0.1,
                        metadata={'cache_hit': True, 'fingerprint': fingerprint}
                    )
            
            # Perform crawl based on depth
            if self.depth == 'shallow':
                context = self._shallow_crawl()
            else:
                context = self._deep_crawl()
            
            # Store patterns in Knowledge Graph
            patterns_created = self._store_patterns(context)
            
            # Save to cache
            if self.cache_manager:
                self.cache_manager.put(
                    self.app_name,
                    self.depth,
                    fingerprint,
                    self._context_to_dict(context)
                )
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            logger.info(f"{self.depth.capitalize()} crawl complete for {self.app_name}: {patterns_created} patterns in {execution_time:.2f}s")
            
            return CrawlerResult(
                crawler_id=self.get_crawler_info()['crawler_id'],
                status=CrawlerStatus.COMPLETED,
                items_discovered=len(context.entry_points),
                patterns_created=patterns_created,
                execution_time=execution_time,
                metadata={
                    'cache_hit': False,
                    'fingerprint': fingerprint,
                    'depth': self.depth
                }
            )
            
        except Exception as e:
            logger.error(f"Application crawl failed for {self.app_name}: {e}", exc_info=True)
            return CrawlerResult(
                crawler_id=self.get_crawler_info()['crawler_id'],
                status=CrawlerStatus.FAILED,
                items_discovered=0,
                patterns_created=0,
                execution_time=(datetime.now() - start_time).total_seconds(),
                error_message=str(e)
            )
    
    def _generate_fingerprint(self) -> str:
        """
        Generate fingerprint for cache invalidation.
        
        Uses git hash if available, otherwise file modification times.
        """
        # Try git hash first (most reliable)
        try:
            result = subprocess.run(
                ['git', 'log', '-1', '--format=%H', '--', str(self.app_path)],
                cwd=self.workspace_path,
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0 and result.stdout.strip():
                git_hash = result.stdout.strip()[:12]
                return f"{self.app_name}_{git_hash}"
        except Exception as e:
            logger.debug(f"Git hash generation failed: {e}")
        
        # Fallback: hash of modification times (sampling)
        timestamps = []
        sample_count = 0
        max_samples = 50
        
        try:
            for file_path in self.app_path.rglob('*'):
                if file_path.is_file() and not any(part.startswith('.') for part in file_path.parts):
                    timestamps.append(str(file_path.stat().st_mtime))
                    sample_count += 1
                    if sample_count >= max_samples:
                        break
            
            combined = ''.join(sorted(timestamps))
            hash_obj = hashlib.md5(combined.encode())
            return f"{self.app_name}_{hash_obj.hexdigest()[:12]}"
        except Exception as e:
            logger.warning(f"Fingerprint generation failed: {e}")
            return f"{self.app_name}_unknown"
    
    def _shallow_crawl(self) -> ApplicationContext:
        """
        Fast shallow crawl (entry points + structure only).
        Target: <10 seconds
        """
        # 1. Find entry points
        entry_points = self._find_entry_points()
        
        # 2. Analyze directory structure (first 2 levels only)
        structure = self._analyze_structure(max_depth=2)
        
        # 3. Parse configuration files
        configuration = self._parse_configurations()
        
        return ApplicationContext(
            app_name=self.app_name,
            entry_points=entry_points,
            structure=structure,
            configuration=configuration
        )
    
    def _deep_crawl(self) -> ApplicationContext:
        """
        Full deep crawl (comprehensive analysis).
        Target: <60 seconds
        """
        # Start with shallow crawl
        shallow_context = self._shallow_crawl()
        
        # 4. Full file inventory
        file_inventory = self._inventory_files()
        
        # 5. Code relationships (imports, dependencies)
        relationships = self._map_relationships()
        
        # 6. Database references
        database_references = self._extract_database_references()
        
        return ApplicationContext(
            app_name=shallow_context.app_name,
            entry_points=shallow_context.entry_points,
            structure=shallow_context.structure,
            configuration=shallow_context.configuration,
            file_inventory=file_inventory,
            relationships=relationships,
            database_references=database_references
        )
    
    def _find_entry_points(self) -> List[Dict[str, Any]]:
        """Find application entry points"""
        entry_points = []
        
        for pattern in self.ENTRY_POINT_PATTERNS:
            for entry_file in self.app_path.rglob(pattern):
                try:
                    entry_points.append({
                        'file': str(entry_file.relative_to(self.app_path)),
                        'type': self._classify_entry_point(entry_file),
                        'size': entry_file.stat().st_size,
                        'modified': datetime.fromtimestamp(entry_file.stat().st_mtime).isoformat()
                    })
                except Exception as e:
                    logger.debug(f"Error processing entry point {entry_file}: {e}")
        
        logger.info(f"Found {len(entry_points)} entry points")
        return entry_points
    
    def _classify_entry_point(self, file_path: Path) -> str:
        """Classify entry point by file type"""
        suffix = file_path.suffix.lower()
        name = file_path.name.lower()
        
        if 'application' in name:
            return 'configuration'
        elif 'index' in name:
            return 'main'
        elif suffix in ['.cfm', '.html']:
            return 'view'
        elif suffix in ['.js', '.py', '.php']:
            return 'controller'
        else:
            return 'unknown'
    
    def _analyze_structure(self, max_depth: int = 2) -> Dict[str, Any]:
        """
        Analyze directory structure.
        
        Args:
            max_depth: Maximum depth to traverse (2 for shallow, unlimited for deep)
        """
        structure = {
            'root': str(self.app_path),
            'directories': [],
            'total_files': 0,
            'file_types': {}
        }
        
        try:
            for root, dirs, files in os.walk(self.app_path):
                # Calculate current depth
                depth = len(Path(root).relative_to(self.app_path).parts)
                
                if depth >= max_depth:
                    dirs.clear()  # Don't recurse deeper
                    continue
                
                # Filter out common ignored directories
                dirs[:] = [d for d in dirs if d not in 
                          ['.git', 'node_modules', 'vendor', '__pycache__', 'venv', 'bin', 'obj']]
                
                # Add directory info
                rel_path = str(Path(root).relative_to(self.app_path))
                if rel_path != '.':
                    structure['directories'].append({
                        'path': rel_path,
                        'file_count': len(files),
                        'depth': depth
                    })
                
                # Count files by type
                structure['total_files'] += len(files)
                for file in files:
                    suffix = Path(file).suffix.lower() or 'no_extension'
                    structure['file_types'][suffix] = structure['file_types'].get(suffix, 0) + 1
        
        except Exception as e:
            logger.error(f"Structure analysis failed: {e}")
        
        return structure
    
    def _parse_configurations(self) -> Dict[str, Any]:
        """Parse configuration files"""
        configurations = {}
        
        for config_file_name in self.CONFIGURATION_FILES:
            config_path = self.app_path / config_file_name
            if config_path.exists():
                try:
                    configurations[config_file_name] = {
                        'exists': True,
                        'size': config_path.stat().st_size,
                        'modified': datetime.fromtimestamp(config_path.stat().st_mtime).isoformat()
                    }
                    
                    # Parse specific config types
                    if config_file_name == 'package.json' and config_path.stat().st_size < 100000:
                        try:
                            with open(config_path, 'r') as f:
                                package_data = json.load(f)
                                configurations[config_file_name]['dependencies'] = list(package_data.get('dependencies', {}).keys())
                        except Exception:
                            pass
                
                except Exception as e:
                    logger.debug(f"Error parsing {config_file_name}: {e}")
        
        return configurations
    
    def _inventory_files(self) -> List[Dict[str, Any]]:
        """Full file inventory (deep mode only)"""
        inventory = []
        
        try:
            for file_path in self.app_path.rglob('*'):
                if not file_path.is_file():
                    continue
                
                # Skip hidden and generated files
                if any(part.startswith('.') for part in file_path.parts):
                    continue
                
                try:
                    inventory.append({
                        'path': str(file_path.relative_to(self.app_path)),
                        'extension': file_path.suffix.lower(),
                        'size': file_path.stat().st_size,
                        'modified': datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                    })
                except Exception as e:
                    logger.debug(f"Error inventorying {file_path}: {e}")
        
        except Exception as e:
            logger.error(f"File inventory failed: {e}")
        
        logger.info(f"Inventoried {len(inventory)} files")
        return inventory
    
    def _map_relationships(self) -> List[Dict[str, Any]]:
        """Map code relationships (deep mode only)"""
        relationships = []
        
        # This would implement relationship detection
        # For now, return placeholder
        logger.info("Relationship mapping (placeholder)")
        return relationships
    
    def _extract_database_references(self) -> List[Dict[str, Any]]:
        """Extract database references (deep mode only)"""
        db_refs = []
        
        # This would implement database reference extraction
        # For now, return placeholder
        logger.info("Database reference extraction (placeholder)")
        return db_refs
    
    def _store_patterns(self, context: ApplicationContext) -> int:
        """Store context as patterns in Knowledge Graph"""
        if not self.knowledge_graph:
            return 0
        
        patterns_created = 0
        
        try:
            # Store application context
            self.knowledge_graph.add_pattern(
                scope='application',
                namespace=self.app_name,
                pattern_type='context',
                data=self._context_to_dict(context),
                confidence=0.90,
                tags=[self.app_name, self.depth, 'application-context']
            )
            patterns_created += 1
        except Exception as e:
            logger.error(f"Failed to store patterns: {e}")
        
        return patterns_created
    
    def _context_to_dict(self, context: ApplicationContext) -> Dict[str, Any]:
        """Convert ApplicationContext to dictionary"""
        return {
            'app_name': context.app_name,
            'entry_points': context.entry_points,
            'structure': context.structure,
            'configuration': context.configuration,
            'file_inventory': context.file_inventory,
            'relationships': context.relationships,
            'database_references': context.database_references,
            'crawl_timestamp': datetime.now().isoformat(),
            'depth': self.depth
        }
