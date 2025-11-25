"""
Multi-Application Orchestrator for CORTEX

Enhanced orchestrator for 2-3 application progressive loading with shared database context.
Optimized for multi-application workspaces with legacy codebases.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import logging
import json
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field

from .workspace_topology_crawler import WorkspaceTopologyCrawler
from .application_scoped_crawler import ApplicationScopedCrawler
from .persistent_cache import PersistentApplicationCache
from .database_inference_engine import DatabaseSchemaInferenceEngine
from .orchestrator import CrawlerOrchestrator, OrchestrationResult
from .base_crawler import CrawlerResult, CrawlerStatus

# Phase 2 imports
from .application_prioritization_engine import ApplicationPrioritizationEngine
from .smart_cache_manager import SmartCacheManager

logger = logging.getLogger(__name__)


@dataclass
class SharedDatabaseSchema:
    """Shared database schema knowledge across all applications"""
    tables: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    relationships: List[Dict[str, Any]] = field(default_factory=list)
    datasources: List[Dict[str, str]] = field(default_factory=list)
    contributing_apps: List[str] = field(default_factory=list)
    last_updated: Optional[str] = None


class SharedDatabaseContextManager:
    """
    Manages shared database knowledge across all applications.
    
    Since all apps use the same Oracle database, CORTEX learns:
    - Table definitions from App A can inform context for App B
    - Common query patterns across applications
    - High-confidence schema from multiple app perspectives
    """
    
    def __init__(self, cache_dir):
        """
        Initialize shared database context manager.
        
        Args:
            cache_dir: Base cache directory (cortex-brain), can be Path or str
        """
        cache_dir = Path(cache_dir) if isinstance(cache_dir, str) else cache_dir
        self.cache_dir = cache_dir / "context-cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.shared_schema_file = self.cache_dir / "shared_database_schema.json"
        self.schema = self._load_shared_schema()
        
        logger.info(f"Initialized shared database context: {len(self.schema.tables)} tables")
    
    def _load_shared_schema(self) -> SharedDatabaseSchema:
        """Load shared schema from cache"""
        if self.shared_schema_file.exists():
            try:
                with open(self.shared_schema_file, 'r') as f:
                    data = json.load(f)
                    return SharedDatabaseSchema(**data)
            except Exception as e:
                logger.warning(f"Failed to load shared schema: {e}")
        
        return SharedDatabaseSchema()
    
    def _save_shared_schema(self) -> None:
        """Save shared schema to cache"""
        try:
            self.schema.last_updated = datetime.now().isoformat()
            
            with open(self.shared_schema_file, 'w') as f:
                json.dump({
                    'tables': self.schema.tables,
                    'relationships': self.schema.relationships,
                    'datasources': self.schema.datasources,
                    'contributing_apps': self.schema.contributing_apps,
                    'last_updated': self.schema.last_updated
                }, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save shared schema: {e}")
    
    def merge_app_schema(self, app_name: str, app_schema: Dict[str, Any]) -> None:
        """
        Merge application-specific schema into shared schema.
        
        Intelligence:
        - Combines table definitions from multiple apps
        - Increases confidence scores when multiple apps reference same table
        - Detects schema conflicts (same table, different columns)
        """
        if app_name not in self.schema.contributing_apps:
            self.schema.contributing_apps.append(app_name)
        
        # Merge tables
        for table_name, table_info in app_schema.get('tables', {}).items():
            if table_name not in self.schema.tables:
                # First time seeing this table
                self.schema.tables[table_name] = {
                    'name': table_name,
                    'columns': table_info.get('columns', []),
                    'primary_key': table_info.get('primary_key'),
                    'relationships': table_info.get('relationships', []),
                    'source_apps': [app_name],
                    'confidence': table_info.get('confidence', 0.5),
                    'operations': table_info.get('operations', [])
                }
            else:
                # Table exists - merge and boost confidence
                existing = self.schema.tables[table_name]
                
                # Merge columns (union)
                existing_cols = set(existing.get('columns', []))
                new_cols = set(table_info.get('columns', []))
                existing['columns'] = list(existing_cols | new_cols)
                
                # Add source app
                if app_name not in existing.get('source_apps', []):
                    existing['source_apps'].append(app_name)
                
                # Confidence boost (multiple apps = higher confidence)
                boost = 0.1 * len(existing['source_apps'])
                existing['confidence'] = min(existing.get('confidence', 0.5) + boost, 1.0)
                
                # Merge operations
                existing_ops = set(existing.get('operations', []))
                new_ops = set(table_info.get('operations', []))
                existing['operations'] = list(existing_ops | new_ops)
                
                # Update primary key if not set
                if not existing.get('primary_key') and table_info.get('primary_key'):
                    existing['primary_key'] = table_info.get('primary_key')
        
        # Merge relationships
        for rel in app_schema.get('relationships', []):
            # Avoid duplicates
            if rel not in self.schema.relationships:
                self.schema.relationships.append(rel)
        
        # Merge datasources
        for ds in app_schema.get('datasources', []):
            if ds not in self.schema.datasources:
                self.schema.datasources.append(ds)
        
        self._save_shared_schema()
        
        logger.info(f"Merged schema from {app_name}: {len(self.schema.tables)} total tables")
    
    def get_table_info(self, table_name: str) -> Optional[Dict[str, Any]]:
        """Get high-confidence table info from shared schema"""
        return self.schema.tables.get(table_name)
    
    def get_related_tables(self, table_name: str) -> List[str]:
        """Find tables related to given table (JOIN patterns)"""
        related = []
        
        for rel in self.schema.relationships:
            if rel.get('source_table') == table_name:
                related.append(rel.get('target_table'))
            elif rel.get('target_table') == table_name:
                related.append(rel.get('source_table'))
        
        return list(set(related))
    
    def get_high_confidence_tables(self) -> List[str]:
        """Get tables with high confidence scores (>=0.8)"""
        return [
            name for name, info in self.schema.tables.items()
            if info.get('confidence', 0) >= 0.8
        ]


class MultiApplicationOrchestrator(CrawlerOrchestrator):
    """
    Specialized orchestrator for multi-application workspaces.
    
    Intelligence:
    1. Detect workspace type (multi-app, monorepo, microservices)
    2. Prioritize applications by:
       - Recent user activity (open files, edits)
       - Git activity
       - Navigation patterns
    3. Progressive loading (top 2 apps immediate, 3rd in background, rest on-demand)
    4. Shared database context management
    5. Cache management (LRU eviction)
    """
    
    def __init__(
        self,
        workspace_path: Path,
        knowledge_graph: Optional[Any] = None,
        cortex_brain_path: Optional[Path] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize multi-application orchestrator.
        
        Args:
            workspace_path: Path to workspace root
            knowledge_graph: KnowledgeGraph instance
            cortex_brain_path: Path to CORTEX brain directory
            config: Optional configuration
        """
        super().__init__(
            workspace_path=workspace_path,
            knowledge_graph=knowledge_graph,
            config=config or {},
            parallel=True,
            max_workers=3  # Optimized for 2-3 apps
        )
        
        # Initialize cache manager
        if cortex_brain_path:
            self.cache_manager = PersistentApplicationCache(
                cache_dir=Path(cortex_brain_path) if isinstance(cortex_brain_path, str) else cortex_brain_path,
                max_cache_size_mb=500,
                ttl_days=7
            )
        else:
            self.cache_manager = None
        
        # Initialize shared database context
        if cortex_brain_path:
            self.shared_db_context = SharedDatabaseContextManager(cortex_brain_path)
        else:
            self.shared_db_context = None
        
        # Phase 2: Initialize activity-based prioritization (NEW)
        self.prioritization_engine = None
        self.smart_cache_manager = None
        
        logger.info("Initialized multi-application orchestrator")
    
    def run_progressive(self) -> OrchestrationResult:
        """
        Execute progressive multi-application crawling.
        
        Optimized for 2-3 app focus with shared database context.
        """
        start_time = datetime.now()
        results = []
        
        try:
            # Phase 1: Fast topology detection (target: 5 seconds)
            logger.info("Phase 1: Detecting workspace topology...")
            topology_crawler = WorkspaceTopologyCrawler({
                'workspace_path': self.workspace_path,
                'knowledge_graph': self.knowledge_graph
            })
            topology_result = topology_crawler.execute()
            results.append(topology_result)
            
            if topology_result.status != CrawlerStatus.COMPLETED:
                raise Exception("Topology detection failed")
            
            # Get topology from knowledge graph
            topology = self._get_topology_from_kg()
            if not topology:
                raise Exception("Failed to retrieve topology from knowledge graph")
            
            applications = topology.get('applications', [])
            logger.info(f"Detected {len(applications)} applications")
            
            if not applications:
                logger.warning("No applications detected")
                return self._build_orchestration_result(start_time, results)
            
            # Phase 1.5: Initialize smart cache manager (Phase 2 feature)
            if not self.smart_cache_manager and self.cache_manager:
                try:
                    cache_config = {
                        'workspace_path': self.workspace_path,
                        'cache_manager': self.cache_manager,
                        'check_interval': 60,  # Check every 60 seconds
                        'promotion_threshold': 5,  # Promote after 5 changes
                        'demotion_threshold': 300  # Demote after 5 min idle
                    }
                    self.smart_cache_manager = SmartCacheManager(cache_config)
                    
                    # Register callbacks
                    self.smart_cache_manager.register_callback(
                        'promotion',
                        lambda app_name, tier: logger.info(f"Cache PROMOTED: {app_name} → {tier}")
                    )
                    self.smart_cache_manager.register_callback(
                        'demotion',
                        lambda app_name, tier: logger.info(f"Cache DEMOTED: {app_name} → {tier}")
                    )
                    self.smart_cache_manager.register_callback(
                        'invalidation',
                        lambda app_name: logger.info(f"Cache INVALIDATED: {app_name}")
                    )
                    
                    # Start filesystem watching
                    self.smart_cache_manager.start()
                    logger.info("Smart cache manager initialized (Phase 2)")
                except Exception as e:
                    logger.warning(f"Failed to initialize smart cache manager: {e}")
            
            # Phase 2: Prioritize applications (target: <1 second)
            logger.info("Phase 2: Prioritizing applications...")
            prioritized_apps = self._prioritize_applications(applications)
            
            # Phase 3: Load immediate-tier applications (target: 15-20 seconds)
            logger.info("Phase 3: Loading immediate-tier applications...")
            immediate_apps = [app for app in prioritized_apps if app.get('priority_tier') == 'immediate']
            if not immediate_apps:
                # Fallback: use top 2-3 if tier not available
                immediate_apps = prioritized_apps[:3]
            
            for app in immediate_apps:
                logger.info(f"Crawling {app['name']} (tier: {app.get('priority_tier', 'unknown')}, score: {app.get('priority_score', 0):.2f})...")
                
                # Crawl with database inference
                app_result = self._crawl_application_with_db_inference(app)
                results.append(app_result)
            
            # Phase 4: Pre-warm queued-tier applications (background)
            queued_apps = [app for app in prioritized_apps if app.get('priority_tier') == 'queued']
            if queued_apps:
                logger.info(f"Phase 4: Pre-warming {len(queued_apps)} queued-tier applications...")
                # Note: Background execution would be implemented with threading
                # For now, we'll pre-cache metadata only
                for app in queued_apps:
                    if self.cache_manager:
                        self.cache_manager.cache_metadata(app['name'], app)
            
            # Phase 5: Queue background-tier apps for lazy loading
            background_apps = [app for app in prioritized_apps if app.get('priority_tier') == 'background']
            if background_apps:
                logger.info(f"Phase 5: Queued {len(background_apps)} background-tier applications for lazy loading")
                # Store in knowledge graph for later retrieval
                self._queue_lazy_apps(background_apps)
            
            return self._build_orchestration_result(start_time, results)
        
        except Exception as e:
            logger.error(f"Progressive crawling failed: {e}", exc_info=True)
            return self._build_orchestration_result(start_time, results, error=str(e))
    
    def load_application_on_demand(
        self,
        app_name: str,
        depth: str = 'shallow'
    ) -> CrawlerResult:
        """
        User-triggered deep dive into specific application.
        Called when user says: "analyze AdjustmentManager"
        
        Args:
            app_name: Application name
            depth: 'shallow' or 'deep'
        
        Returns:
            CrawlerResult
        """
        logger.info(f"On-demand loading: {app_name} (depth={depth})")
        
        app_path = self.workspace_path / app_name
        if not app_path.exists():
            logger.error(f"Application not found: {app_name}")
            return CrawlerResult(
                crawler_id=f'on_demand_{app_name}',
                status=CrawlerStatus.FAILED,
                items_discovered=0,
                patterns_created=0,
                execution_time=0,
                error_message=f"Application not found: {app_name}"
            )
        
        # Crawl with database inference
        app_info = {'name': app_name, 'path': str(app_path)}
        return self._crawl_application_with_db_inference(app_info, depth=depth)
    
    def _get_topology_from_kg(self) -> Optional[Dict[str, Any]]:
        """Retrieve topology from knowledge graph"""
        if not self.knowledge_graph:
            return None
        
        try:
            # Query knowledge graph for workspace topology pattern
            patterns = self.knowledge_graph.search_patterns(
                scope='workspace',
                namespace='topology'
            )
            
            if patterns:
                return patterns[0].get('data', {})
        except Exception as e:
            logger.error(f"Failed to retrieve topology: {e}")
        
        return None
    
    def _prioritize_applications(self, applications: List[Dict]) -> List[Dict]:
        """
        Prioritize applications by relevance using Phase 2 intelligence.
        
        Phase 2 Enhancement: Uses ApplicationPrioritizationEngine for intelligent
        multi-signal prioritization (filesystem + git + access + dependency).
        
        Fallback: If Phase 2 not available, uses legacy scoring.
        """
        # Try Phase 2 intelligent prioritization
        try:
            if not self.prioritization_engine:
                # Initialize prioritization engine
                config = {
                    'workspace_path': self.workspace_path,
                    'applications': applications,
                    'immediate_count': 3,
                    'queued_count': 5
                }
                self.prioritization_engine = ApplicationPrioritizationEngine(config)
            
            # Get prioritized applications
            priorities = self.prioritization_engine.prioritize_applications()
            
            # Convert to dictionary format with priority scores
            prioritized = []
            for priority in priorities:
                # Find matching application
                app = next((a for a in applications if a['name'] == priority.name), None)
                if app:
                    prioritized.append({
                        **app,
                        'priority_score': priority.normalized_score,
                        'priority_tier': priority.tier,
                        'priority_rank': priority.priority_rank
                    })
            
            logger.info(f"Phase 2 prioritization: {len(prioritized)} applications ranked")
            return prioritized
        
        except Exception as e:
            logger.warning(f"Phase 2 prioritization failed, using legacy method: {e}")
            return self._prioritize_applications_legacy(applications)
    
    def _prioritize_applications_legacy(self, applications: List[Dict]) -> List[Dict]:
        """
        Legacy prioritization method (Phase 1).
        
        Scoring factors:
        - Open files in VS Code (40 points each)
        - Recent edits (30 points per edit in last 7 days)
        - Estimated size (smaller = higher priority, 20 points max)
        - Has database access (10 points)
        """
        scored_apps = []
        
        for app in applications:
            score = 0
            app_path = Path(app['path'])
            
            # TODO: Implement VS Code integration for open files
            # For now, use placeholder
            open_files_count = 0
            score += open_files_count * 40
            
            # Git activity (use last_modified as proxy)
            try:
                last_modified = datetime.fromisoformat(app.get('last_modified', ''))
                days_since_modified = (datetime.now() - last_modified).days
                if days_since_modified <= 7:
                    score += 30 * (7 - days_since_modified)
            except Exception:
                pass
            
            # Size score (smaller = higher priority for faster initial load)
            size_mb = app.get('estimated_size', 0) / (1024 * 1024)
            size_score = max(0, 20 - (size_mb / 10))  # Normalize
            score += size_score
            
            # Database access
            if app.get('has_database_access'):
                score += 10
            
            scored_apps.append({
                **app,
                'priority_score': score
            })
        
        # Sort by priority score (highest first)
        scored_apps.sort(key=lambda x: x.get('priority_score', 0), reverse=True)
        
        # Log top 3 apps
        top_3 = ', '.join([f"{a['name']} ({a.get('priority_score', 0):.1f})" for a in scored_apps[:3]])
        logger.info(f"Prioritized applications: {top_3}")
        
        return scored_apps
    
    def _crawl_application_with_db_inference(
        self,
        app_info: Dict[str, Any],
        depth: str = 'shallow'
    ) -> CrawlerResult:
        """
        Crawl application with database schema inference.
        
        Args:
            app_info: Application information dictionary
            depth: 'shallow' or 'deep'
        
        Returns:
            CrawlerResult with database schema information
        """
        app_name = app_info['name']
        app_path = Path(app_info['path'])
        
        try:
            # Crawl application
            app_crawler = ApplicationScopedCrawler({
                'workspace_path': self.workspace_path,
                'application_name': app_name,
                'depth': depth,
                'knowledge_graph': self.knowledge_graph,
                'cache_manager': self.cache_manager
            })
            
            result = app_crawler.execute()
            
            # If successful, infer database schema
            if result.status == CrawlerStatus.COMPLETED and self.shared_db_context:
                logger.info(f"Inferring database schema for {app_name}...")
                
                db_engine = DatabaseSchemaInferenceEngine(app_path)
                db_schema = db_engine.infer_schema()
                
                # Merge into shared database context
                self.shared_db_context.merge_app_schema(app_name, db_schema)
                
                # Add database info to metadata
                result.metadata['database_schema'] = {
                    'total_tables': db_schema.get('total_tables', 0),
                    'high_confidence_tables': db_schema.get('high_confidence_tables', 0)
                }
            
            return result
        
        except Exception as e:
            logger.error(f"Application crawl with DB inference failed for {app_name}: {e}")
            return CrawlerResult(
                crawler_id=f'app_crawler_{app_name}',
                status=CrawlerStatus.FAILED,
                items_discovered=0,
                patterns_created=0,
                execution_time=0,
                error_message=str(e)
            )
    
    def _queue_lazy_apps(self, apps: List[Dict[str, Any]]) -> None:
        """Queue applications for lazy loading"""
        if not self.knowledge_graph:
            return
        
        try:
            self.knowledge_graph.add_pattern(
                scope='workspace',
                namespace='lazy_queue',
                pattern_type='queue',
                data={
                    'applications': [app['name'] for app in apps],
                    'queued_at': datetime.now().isoformat()
                },
                confidence=1.0,
                tags=['lazy-loading', 'queue']
            )
            logger.info(f"Queued {len(apps)} applications for lazy loading")
        except Exception as e:
            logger.error(f"Failed to queue lazy apps: {e}")
    
    def _build_orchestration_result(
        self,
        start_time: datetime,
        results: List[CrawlerResult],
        error: Optional[str] = None
    ) -> OrchestrationResult:
        """Build orchestration result from crawler results"""
        completed_at = datetime.now()
        duration = (completed_at - start_time).total_seconds()
        
        completed = sum(1 for r in results if r.status == CrawlerStatus.COMPLETED)
        failed = sum(1 for r in results if r.status == CrawlerStatus.FAILED)
        total_items = sum(r.items_discovered for r in results)
        total_patterns = sum(r.patterns_created for r in results)
        
        return OrchestrationResult(
            started_at=start_time,
            completed_at=completed_at,
            duration_seconds=duration,
            total_crawlers=len(results),
            completed=completed,
            failed=failed,
            skipped=0,
            total_items_discovered=total_items,
            total_patterns_created=total_patterns,
            crawler_results=results,
            errors=[error] if error else []
        )
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        if self.cache_manager:
            return self.cache_manager.get_stats()
        return {}
    
    def get_shared_database_info(self) -> Dict[str, Any]:
        """Get shared database schema information"""
        if self.shared_db_context:
            return {
                'total_tables': len(self.shared_db_context.schema.tables),
                'high_confidence_tables': len(self.shared_db_context.get_high_confidence_tables()),
                'contributing_apps': self.shared_db_context.schema.contributing_apps,
                'relationships_count': len(self.shared_db_context.schema.relationships),
                'datasources': self.shared_db_context.schema.datasources
            }
        return {}
    
    def cleanup(self):
        """
        Cleanup resources (Phase 2 enhancement).
        
        Call this when done with the orchestrator to stop
        filesystem watching and release resources.
        """
        if self.smart_cache_manager:
            try:
                self.smart_cache_manager.stop()
                logger.info("Smart cache manager stopped")
            except Exception as e:
                logger.warning(f"Error stopping smart cache manager: {e}")
        
        if self.shared_db_context:
            try:
                self.shared_db_context.save()
                logger.info("Shared database context saved")
            except Exception as e:
                logger.warning(f"Error saving shared database context: {e}")
