"""
Brain Initialization Setup Module

Initializes CORTEX brain databases (Tier 1, 2, 3) and knowledge graph.

SOLID Principles:
- Single Responsibility: Only handles brain initialization
- Open/Closed: Extends BaseOperationModule without modifying it
- Dependency Inversion: Depends on BaseOperationModule abstraction

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

from pathlib import Path
from typing import Dict, Any, Tuple, List
from datetime import datetime
import sqlite3
import yaml

from src.operations.base_operation_module import (
    BaseOperationModule,
    OperationModuleMetadata,
    OperationResult,
    OperationStatus,
    OperationPhase
)


class BrainInitializationModule(BaseOperationModule):
    """
    Setup module for initializing CORTEX brain.
    
    Responsibilities:
    1. Initialize Tier 1 (SQLite database for conversation history)
    2. Initialize Tier 2 (YAML knowledge graph)
    3. Initialize Tier 3 (Development context)
    4. Create required directories
    5. Verify brain health
    """
    
    def get_metadata(self) -> OperationModuleMetadata:
        """Return module metadata."""
        return OperationModuleMetadata(
            module_id="brain_initialization",
            name="Brain Database Initialization",
            description="Initialize Tier 1, 2, 3 brain databases and knowledge graph",
            phase=OperationPhase.FEATURES,
            priority=30,
            dependencies=["python_dependencies"],
            optional=False,
        )
    
    def validate_prerequisites(self, context: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate prerequisites for brain initialization.
        
        Checks:
        1. Project root exists
        2. cortex-brain directory exists or can be created
        3. Required Python packages available (PyYAML, sqlite3)
        """
        issues = []
        
        # Check project root
        project_root = context.get('project_root')
        if not project_root:
            issues.append("Project root not found in context")
            return False, issues
        
        project_root = Path(project_root)
        
        # Check cortex-brain directory
        brain_dir = project_root / "cortex-brain"
        if not brain_dir.exists():
            # Check if we can create it
            try:
                brain_dir.mkdir(parents=True, exist_ok=True)
                self.log_info(f"Created cortex-brain directory: {brain_dir}")
            except Exception as e:
                issues.append(f"Cannot create cortex-brain directory: {e}")
                return False, issues
        
        # Verify PyYAML available
        try:
            import yaml
        except ImportError:
            issues.append("PyYAML not installed (required for Tier 2)")
        
        return len(issues) == 0, issues
    
    def execute(self, context: Dict[str, Any]) -> OperationResult:
        """
        Execute brain initialization.
        
        Steps:
        1. Initialize Tier 1 database
        2. Initialize Tier 2 knowledge graph
        3. Initialize Tier 3 context
        4. Verify brain health
        5. Update context
        """
        start_time = datetime.now()
        warnings = []
        
        try:
            project_root = Path(context['project_root'])
            brain_dir = project_root / "cortex-brain"
            
            self.log_info("Initializing CORTEX brain...")
            
            # Initialize Tier 1 (Conversation History)
            tier1_result = self._initialize_tier1(brain_dir)
            if not tier1_result['success']:
                return OperationResult(
                success=False,
                    status=OperationStatus.FAILED,
                    message="Tier 1 initialization failed",
                    errors=[tier1_result.get('error', 'Unknown error')],
                    duration_seconds=(datetime.now() - start_time).total_seconds()
                )
            self.log_info(f"✓ Tier 1: {tier1_result['message']}")
            
            # Initialize Tier 2 (Knowledge Graph)
            tier2_result = self._initialize_tier2(brain_dir)
            if not tier2_result['success']:
                warnings.append(f"Tier 2: {tier2_result.get('error', 'Failed')}")
                self.log_warning(warnings[0])
            else:
                self.log_info(f"✓ Tier 2: {tier2_result['message']}")
            
            # Initialize Tier 3 (Development Context)
            tier3_result = self._initialize_tier3(brain_dir)
            if not tier3_result['success']:
                warnings.append(f"Tier 3: {tier3_result.get('error', 'Failed')}")
                self.log_warning(warnings[-1])
            else:
                self.log_info(f"✓ Tier 3: {tier3_result['message']}")
            
            # Update context
            context['brain_initialized'] = True
            context['brain_dir'] = str(brain_dir)
            context['tier1_db'] = str(brain_dir / "conversation-history.db")
            context['tier2_kg'] = str(brain_dir / "knowledge-graph.yaml")
            context['tier3_context'] = str(brain_dir / "development-context.yaml")
            
            duration_seconds = (datetime.now() - start_time).total_seconds()
            
            status = OperationStatus.WARNING if warnings else OperationStatus.SUCCESS
            message = "Brain initialized successfully" if not warnings else "Brain initialized with warnings"
            
            return OperationResult(
                success=True,
                status=status,
                message=message,
                data={
                    'brain_dir': str(brain_dir),
                    'tier1': tier1_result,
                    'tier2': tier2_result,
                    'tier3': tier3_result
                },
                warnings=warnings,
                duration_seconds=duration_seconds
            )
            
        except Exception as e:
            self.log_error(f"Brain initialization failed: {e}")
            return OperationResult(
                success=False,
                status=OperationStatus.FAILED,
                message=f"Brain initialization failed: {str(e)}",
                errors=[str(e)],
                duration_seconds=(datetime.now() - start_time).total_seconds()
            )
    
    def _initialize_tier1(self, brain_dir: Path) -> Dict[str, Any]:
        """
        Initialize Tier 1 (Conversation History Database).
        
        Args:
            brain_dir: Path to cortex-brain directory
        
        Returns:
            Result dictionary with success status
        """
        try:
            db_path = brain_dir / "conversation-history.db"
            
            # Check if already exists
            if db_path.exists():
                # Verify it's a valid SQLite database
                try:
                    conn = sqlite3.connect(str(db_path))
                    cursor = conn.cursor()
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                    tables = cursor.fetchall()
                    conn.close()
                    
                    if len(tables) > 0:
                        return {
                            'success': True,
                            'message': f'Database exists ({len(tables)} tables)',
                            'db_path': str(db_path)
                        }
                except:
                    # Database corrupt, will recreate
                    pass
            
            # Create new database
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            # Create conversations table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id TEXT UNIQUE NOT NULL,
                    timestamp TEXT NOT NULL,
                    user_message TEXT,
                    assistant_response TEXT,
                    context TEXT,
                    metadata TEXT
                )
            ''')
            
            # Create index
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_conversation_id 
                ON conversations(conversation_id)
            ''')
            
            conn.commit()
            conn.close()
            
            return {
                'success': True,
                'message': 'Database created',
                'db_path': str(db_path)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _initialize_tier2(self, brain_dir: Path) -> Dict[str, Any]:
        """
        Initialize Tier 2 (Knowledge Graph).
        
        Args:
            brain_dir: Path to cortex-brain directory
        
        Returns:
            Result dictionary with success status
        """
        try:
            kg_path = brain_dir / "knowledge-graph.yaml"
            
            # Check if already exists
            if kg_path.exists():
                try:
                    with open(kg_path, 'r') as f:
                        data = yaml.safe_load(f) or {}
                    
                    return {
                        'success': True,
                        'message': f'Knowledge graph exists ({len(data)} top-level keys)',
                        'kg_path': str(kg_path)
                    }
                except:
                    pass
            
            # Create new knowledge graph
            initial_kg = {
                'version': '1.0',
                'created': datetime.now().isoformat(),
                'patterns': {},
                'lessons_learned': {},
                'capabilities': {},
                'architectural_patterns': {},
                'file_relationships': {}
            }
            
            with open(kg_path, 'w') as f:
                yaml.dump(initial_kg, f, default_flow_style=False, sort_keys=False)
            
            return {
                'success': True,
                'message': 'Knowledge graph created',
                'kg_path': str(kg_path)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _initialize_tier3(self, brain_dir: Path) -> Dict[str, Any]:
        """
        Initialize Tier 3 (Development Context).
        
        Args:
            brain_dir: Path to cortex-brain directory
        
        Returns:
            Result dictionary with success status
        """
        try:
            context_path = brain_dir / "development-context.yaml"
            
            # Check if already exists
            if context_path.exists():
                try:
                    with open(context_path, 'r') as f:
                        data = yaml.safe_load(f) or {}
                    
                    return {
                        'success': True,
                        'message': 'Development context exists',
                        'context_path': str(context_path)
                    }
                except:
                    pass
            
            # Create new development context
            initial_context = {
                'version': '1.0',
                'created': datetime.now().isoformat(),
                'project_metrics': {
                    'total_files': 0,
                    'total_lines': 0,
                    'test_coverage': 0.0
                },
                'recent_changes': [],
                'active_branches': [],
                'deployment_info': {}
            }
            
            with open(context_path, 'w') as f:
                yaml.dump(initial_context, f, default_flow_style=False, sort_keys=False)
            
            return {
                'success': True,
                'message': 'Development context created',
                'context_path': str(context_path)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

