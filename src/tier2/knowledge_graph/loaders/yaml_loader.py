"""
YAML Knowledge File Loader

Loads knowledge files from cortex-brain/knowledge/ into Tier 2 database.
Supports on-demand loading with version tracking and incremental updates.

Copyright (c) 2024-2025 Asif Hussain. All rights reserved.
"""

import yaml
import json
import hashlib
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class YAMLKnowledgeLoader:
    """Loads YAML knowledge files into Tier 2 Knowledge Graph."""
    
    def __init__(self, connection_manager, knowledge_base_path: Optional[Path] = None):
        """
        Initialize YAML knowledge loader.
        
        Args:
            connection_manager: Tier 2 ConnectionManager instance
            knowledge_base_path: Path to cortex-brain/knowledge/ directory
        """
        self.connection_manager = connection_manager
        
        # Determine root path
        root = Path(__file__).parent.parent.parent.parent.parent
        
        if knowledge_base_path is None:
            # Default: cortex-brain/knowledge/
            knowledge_base_path = root / "cortex-brain" / "knowledge"
        
        self.knowledge_base_path = Path(knowledge_base_path)
        
        # Additional knowledge library path for user-added content
        self.knowledge_library_path = root / "cortex-brain" / "knowledge-library"
        
        self.loaded_files: Set[str] = set()
        
        logger.info(f"📚 YAML Knowledge Loader initialized: {self.knowledge_base_path}")
        if self.knowledge_library_path.exists():
            logger.info(f"📚 Knowledge Library also available: {self.knowledge_library_path}")
    
    def load_all_knowledge_files(self, force_reload: bool = False) -> Dict[str, int]:
        """
        Load all YAML knowledge files into Tier 2 database.
        
        Args:
            force_reload: If True, reload even if files already loaded
        
        Returns:
            Dictionary with load statistics per category
        """
        if not self.knowledge_base_path.exists():
            logger.warning(f"Knowledge base not found: {self.knowledge_base_path}")
            return {}
        
        stats = {}
        categories = ['engineering', 'testing', 'security', 'devops', 'domains', 'performance', 'ddd']
        
        # Load from primary knowledge base
        for category in categories:
            category_path = self.knowledge_base_path / category
            if not category_path.exists():
                continue
            
            yaml_files = list(category_path.glob("*.yaml"))
            patterns_loaded = 0
            
            for yaml_file in yaml_files:
                file_key = str(yaml_file.relative_to(self.knowledge_base_path))
                
                # Skip if already loaded (unless force_reload)
                if not force_reload and file_key in self.loaded_files:
                    continue
                
                # Check if file has been modified since last load
                if not force_reload and self._is_file_loaded(yaml_file):
                    logger.debug(f"⏭️  Skipping {yaml_file.name} (already loaded, no changes)")
                    continue
                
                count = self._load_yaml_file(yaml_file, category)
                patterns_loaded += count
                self.loaded_files.add(file_key)
            
            if patterns_loaded > 0:
                stats[category] = patterns_loaded
                logger.info(f"✅ Loaded {category}: {patterns_loaded} patterns")
        
        # Load from knowledge-library (user-added content)
        library_stats = self._load_knowledge_library(force_reload)
        stats.update(library_stats)
        
        return stats
    
    def load_category(self, category: str, force_reload: bool = False) -> int:
        """
        Load all YAML files from a specific category.
        
        Args:
            category: Category name (e.g., 'engineering', 'testing')
            force_reload: If True, reload even if files already loaded
        
        Returns:
            Number of patterns loaded
        """
        category_path = self.knowledge_base_path / category
        if not category_path.exists():
            logger.warning(f"Category not found: {category}")
            return 0
        
        patterns_loaded = 0
        yaml_files = list(category_path.glob("*.yaml"))
        
        for yaml_file in yaml_files:
            file_key = str(yaml_file.relative_to(self.knowledge_base_path))
            
            if not force_reload and file_key in self.loaded_files:
                continue
            
            if not force_reload and self._is_file_loaded(yaml_file):
                continue
            
            count = self._load_yaml_file(yaml_file, category)
            patterns_loaded += count
            self.loaded_files.add(file_key)
        
        logger.info(f"✅ Loaded {category}: {patterns_loaded} patterns")
        return patterns_loaded
    
    def load_file(self, file_path: Path, category: Optional[str] = None) -> int:
        """
        Load a specific YAML knowledge file.
        
        Args:
            file_path: Path to YAML file
            category: Category override (auto-detected from path if None)
        
        Returns:
            Number of patterns loaded
        """
        if not file_path.exists():
            logger.error(f"File not found: {file_path}")
            return 0
        
        # Auto-detect category from path
        if category is None:
            try:
                relative_path = file_path.relative_to(self.knowledge_base_path)
                category = relative_path.parts[0] if len(relative_path.parts) > 1 else 'general'
            except ValueError:
                category = 'general'
        
        count = self._load_yaml_file(file_path, category)
        file_key = str(file_path.relative_to(self.knowledge_base_path))
        self.loaded_files.add(file_key)
        
        logger.info(f"✅ Loaded {file_path.name}: {count} patterns")
        return count
    
    def _load_yaml_file(self, file_path: Path, category: str) -> int:
        """
        Load patterns from a single YAML file.
        
        Args:
            file_path: Path to YAML file
            category: Category name
        
        Returns:
            Number of patterns inserted/updated
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            if not isinstance(data, dict):
                logger.warning(f"Invalid YAML structure in {file_path.name}")
                return 0
            
            # Extract patterns based on YAML structure
            patterns = self._extract_patterns_from_yaml(data, file_path, category)
            
            # Store patterns in database
            patterns_loaded = 0
            with self.connection_manager.transaction() as conn:
                cursor = conn.cursor()
                
                for pattern in patterns:
                    # Check if pattern exists
                    cursor.execute(
                        "SELECT id FROM patterns WHERE pattern_id = ?",
                        (pattern['pattern_id'],)
                    )
                    existing = cursor.fetchone()
                    
                    if existing:
                        # Update existing pattern
                        cursor.execute("""
                            UPDATE patterns 
                            SET content = ?, confidence = ?, metadata = ?, 
                                last_accessed = ?
                            WHERE pattern_id = ?
                        """, (
                            pattern['content'],
                            pattern['confidence'],
                            pattern['metadata'],
                            datetime.now().isoformat(),
                            pattern['pattern_id']
                        ))
                    else:
                        # Insert new pattern
                        cursor.execute("""
                            INSERT INTO patterns (
                                pattern_id, title, content, pattern_type, confidence,
                                created_at, last_accessed, access_count, source,
                                metadata, is_pinned, scope, namespaces
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            pattern['pattern_id'],
                            pattern['title'],
                            pattern['content'],
                            pattern['pattern_type'],
                            pattern['confidence'],
                            pattern['created_at'],
                            pattern['last_accessed'],
                            pattern['access_count'],
                            pattern['source'],
                            pattern['metadata'],
                            pattern['is_pinned'],
                            pattern['scope'],
                            pattern['namespaces']
                        ))
                    
                    patterns_loaded += 1
                
                # Store file load metadata
                self._record_file_load(cursor, file_path)
            
            return patterns_loaded
        
        except Exception as e:
            logger.error(f"Failed to load {file_path.name}: {e}")
            return 0
    
    def _extract_patterns_from_yaml(
        self, 
        data: Dict[str, Any], 
        file_path: Path,
        category: str
    ) -> List[Dict[str, Any]]:
        """
        Extract patterns from YAML data structure.
        
        Handles different YAML schemas (design patterns, TDD practices, SOLID, etc.)
        
        Args:
            data: Parsed YAML data
            file_path: Source file path
            category: Category name
        
        Returns:
            List of pattern dictionaries
        """
        patterns = []
        metadata = data.get('metadata', {})
        file_stem = file_path.stem
        
        # Strategy 1: Extract from pattern_selection_guide (design-patterns.yaml)
        if 'pattern_selection_guide' in data:
            patterns.extend(self._extract_pattern_guide(
                data['pattern_selection_guide'],
                file_stem,
                category,
                metadata
            ))
        
        # Strategy 2: Extract from creational/structural/behavioral patterns
        pattern_categories = ['creational_patterns', 'structural_patterns', 'behavioral_patterns']
        for pattern_cat in pattern_categories:
            if pattern_cat in data:
                patterns.extend(self._extract_gof_patterns(
                    data[pattern_cat],
                    file_stem,
                    category,
                    metadata
                ))
        
        # Strategy 3: Extract SOLID principles
        if 'single_responsibility_principle' in data:
            patterns.extend(self._extract_solid_principles(data, file_stem, category, metadata))
        
        # Strategy 4: Extract TDD best practices
        if 'three_laws' in data or 'red_green_refactor' in data:
            patterns.extend(self._extract_tdd_practices(data, file_stem, category, metadata))
        
        # Strategy 5: Extract security practices (OWASP, secure coding)
        if 'owasp_top_10' in data or 'secure_coding_practices' in data:
            patterns.extend(self._extract_security_practices(data, file_stem, category, metadata))
        
        # Strategy 6: Generic extraction (fallback)
        if not patterns:
            patterns.extend(self._extract_generic_patterns(data, file_stem, category, metadata))
        
        return patterns
    
    def _extract_pattern_guide(
        self,
        guide_data: Dict[str, Any],
        file_stem: str,
        category: str,
        metadata: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Extract patterns from pattern_selection_guide structure."""
        patterns = []
        
        for problem_domain, problems in guide_data.items():
            if not isinstance(problems, list):
                continue
            
            for problem_entry in problems:
                pattern_name = problem_entry.get('pattern', '')
                problem_desc = problem_entry.get('problem', '')
                pattern_category = problem_entry.get('category', 'general')
                
                if not pattern_name:
                    continue
                
                pattern_id = self._generate_pattern_id(file_stem, pattern_name)
                
                patterns.append({
                    'pattern_id': pattern_id,
                    'title': f"{pattern_name} Pattern",
                    'content': json.dumps({
                        'problem': problem_desc,
                        'pattern': pattern_name,
                        'domain': problem_domain,
                        'category': pattern_category
                    }),
                    'pattern_type': 'design_pattern',
                    'confidence': 1.0,
                    'created_at': datetime.now().isoformat(),
                    'last_accessed': datetime.now().isoformat(),
                    'access_count': 0,
                    'source': f"knowledge/{category}/{file_stem}.yaml",
                    'metadata': json.dumps({
                        'version': metadata.get('version', '1.0.0'),
                        'author': metadata.get('author', 'Unknown')
                }),
                'is_pinned': 1,
                'scope': 'cortex',
                'namespaces': json.dumps([f"{category}", "design-patterns", pattern_category])
            })
        
        return patterns
    
    def _extract_gof_patterns(
        self,
        patterns_data: List[Dict[str, Any]],
        file_stem: str,
        category: str,
        metadata: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Extract GoF design patterns (creational/structural/behavioral)."""
        patterns = []
        
        for pattern_entry in patterns_data:
            if not isinstance(pattern_entry, dict):
                continue
            
            pattern_name = pattern_entry.get('name', '')
            intent = pattern_entry.get('intent', '')
            problem = pattern_entry.get('problem', '')
            solution = pattern_entry.get('solution', '')
            
            if not pattern_name:
                continue
            
            pattern_id = self._generate_pattern_id(file_stem, pattern_name)
            
            patterns.append({
                'pattern_id': pattern_id,
                'title': pattern_name,
                'content': json.dumps({
                    'intent': intent,
                    'problem': problem,
                    'solution': solution,
                    'consequences': pattern_entry.get('consequences', {}),
                    'implementation': pattern_entry.get('implementation', {})
                }),
                'pattern_type': 'design_pattern',
                'confidence': 1.0,
                'created_at': datetime.now().isoformat(),
                'last_accessed': datetime.now().isoformat(),
                'access_count': 0,
                'source': f"knowledge/{category}/{file_stem}.yaml",
                'metadata': json.dumps(metadata),
                'is_pinned': 1,
                'scope': 'cortex',
                'namespaces': json.dumps([category, "design-patterns", "gof"])
            })
        
        return patterns
    
    def _extract_solid_principles(
        self,
        data: Dict[str, Any],
        file_stem: str,
        category: str,
        metadata: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Extract SOLID principles."""
        patterns = []
        solid_keys = [
            'single_responsibility_principle',
            'open_closed_principle',
            'liskov_substitution_principle',
            'interface_segregation_principle',
            'dependency_inversion_principle'
        ]
        
        for key in solid_keys:
            if key not in data:
                continue
            
            principle_data = data[key]
            principle_name = principle_data.get('name', key.replace('_', ' ').title())
            
            pattern_id = self._generate_pattern_id(file_stem, key)
            
            patterns.append({
                'pattern_id': pattern_id,
                'title': principle_name,
                'content': json.dumps({
                    'definition': principle_data.get('definition', ''),
                    'explanation': principle_data.get('explanation', ''),
                    'violations': principle_data.get('violations', []),
                    'compliance': principle_data.get('compliance', [])
                }),
                'pattern_type': 'principle',
                'confidence': 1.0,
                'created_at': datetime.now().isoformat(),
                'last_accessed': datetime.now().isoformat(),
                'access_count': 0,
                'source': f"knowledge/{category}/{file_stem}.yaml",
                'metadata': json.dumps(metadata),
                'is_pinned': 1,
                'scope': 'cortex',
                'namespaces': json.dumps([category, "solid", "principles"])
            })
        
        return patterns
    
    def _extract_tdd_practices(
        self,
        data: Dict[str, Any],
        file_stem: str,
        category: str,
        metadata: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Extract TDD best practices."""
        patterns = []
        
        # Three Laws of TDD
        if 'three_laws' in data:
            laws = data['three_laws']
            for law_key, law_data in laws.items():
                if not isinstance(law_data, dict):
                    continue
                
                pattern_id = self._generate_pattern_id(file_stem, law_key)
                
                patterns.append({
                    'pattern_id': pattern_id,
                    'title': law_data.get('statement', law_key.replace('_', ' ').title()),
                    'content': json.dumps({
                        'statement': law_data.get('statement', ''),
                        'explanation': law_data.get('explanation', ''),
                        'violation_example': law_data.get('violation_example', {})
                    }),
                    'pattern_type': 'tdd_practice',
                    'confidence': 1.0,
                    'created_at': datetime.now().isoformat(),
                    'last_accessed': datetime.now().isoformat(),
                    'access_count': 0,
                    'source': f"knowledge/{category}/{file_stem}.yaml",
                    'metadata': json.dumps(metadata),
                    'is_pinned': 1,
                    'scope': 'cortex',
                    'namespaces': json.dumps([category, "tdd", "best-practices"])
                })
        
        # RED-GREEN-REFACTOR cycle
        if 'red_green_refactor' in data:
            cycle_data = data['red_green_refactor']
            for phase_key, phase_data in cycle_data.items():
                if not isinstance(phase_data, dict):
                    continue
                
                pattern_id = self._generate_pattern_id(file_stem, f"rgr_{phase_key}")
                
                patterns.append({
                    'pattern_id': pattern_id,
                    'title': f"TDD {phase_key.upper()} Phase",
                    'content': json.dumps(phase_data),
                    'pattern_type': 'tdd_practice',
                    'confidence': 1.0,
                    'created_at': datetime.now().isoformat(),
                    'last_accessed': datetime.now().isoformat(),
                    'access_count': 0,
                    'source': f"knowledge/{category}/{file_stem}.yaml",
                    'metadata': json.dumps(metadata),
                    'is_pinned': 1,
                    'scope': 'cortex',
                    'namespaces': json.dumps([category, "tdd", "red-green-refactor"])
                })
        
        return patterns
    
    def _extract_security_practices(
        self,
        data: Dict[str, Any],
        file_stem: str,
        category: str,
        metadata: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Extract security best practices (OWASP, secure coding)."""
        patterns = []
        
        # OWASP Top 10
        if 'owasp_top_10' in data:
            for vuln_key, vuln_data in data['owasp_top_10'].items():
                if not isinstance(vuln_data, dict):
                    continue
                
                pattern_id = self._generate_pattern_id(file_stem, vuln_key)
                
                patterns.append({
                    'pattern_id': pattern_id,
                    'title': vuln_data.get('name', vuln_key.replace('_', ' ').title()),
                    'content': json.dumps(vuln_data),
                    'pattern_type': 'security_practice',
                    'confidence': 1.0,
                    'created_at': datetime.now().isoformat(),
                    'last_accessed': datetime.now().isoformat(),
                    'access_count': 0,
                    'source': f"knowledge/{category}/{file_stem}.yaml",
                    'metadata': json.dumps(metadata),
                    'is_pinned': 1,
                    'scope': 'cortex',
                    'namespaces': json.dumps([category, "security", "owasp"])
                })
        
        return patterns
    
    def _extract_generic_patterns(
        self,
        data: Dict[str, Any],
        file_stem: str,
        category: str,
        metadata: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generic pattern extraction (fallback)."""
        patterns = []
        
        # Extract top-level sections as patterns (excluding metadata)
        for key, value in data.items():
            if key == 'metadata':
                continue
            
            if not isinstance(value, (dict, list)):
                continue
            
            pattern_id = self._generate_pattern_id(file_stem, key)
            
            patterns.append({
                'pattern_id': pattern_id,
                'title': key.replace('_', ' ').title(),
                'content': json.dumps(value) if isinstance(value, (dict, list)) else str(value),
                'pattern_type': category,
                'confidence': 0.8,
                'created_at': datetime.now().isoformat(),
                'last_accessed': datetime.now().isoformat(),
                'access_count': 0,
                'source': f"knowledge/{category}/{file_stem}.yaml",
                'metadata': json.dumps(metadata),
                'is_pinned': 0,
                'scope': 'cortex',
                'namespaces': json.dumps([category, "knowledge"])
            })
        
        return patterns
    
    # ==================== Knowledge Library Support ====================
    
    def _load_knowledge_library(self, force_reload: bool = False) -> Dict[str, int]:
        """
        Load YAML files from cortex-brain/knowledge-library/ directory.
        
        This directory contains user-added knowledge files organized by category.
        Supports categories: architecture, design-patterns, security
        
        Args:
            force_reload: If True, reload even if files already loaded
        
        Returns:
            Dictionary with load statistics per category
        """
        if not self.knowledge_library_path.exists():
            logger.debug(f"Knowledge library not found: {self.knowledge_library_path}")
            return {}
        
        stats = {}
        library_categories = ['architecture', 'design-patterns', 'security']
        
        for category in library_categories:
            category_path = self.knowledge_library_path / category
            if not category_path.exists():
                continue
            
            yaml_files = list(category_path.glob("*.yaml"))
            patterns_loaded = 0
            
            for yaml_file in yaml_files:
                file_key = f"library:{yaml_file.relative_to(self.knowledge_library_path)}"
                
                # Skip if already loaded (unless force_reload)
                if not force_reload and file_key in self.loaded_files:
                    continue
                
                # Check if file has been modified since last load
                if not force_reload and self._is_file_loaded(yaml_file):
                    logger.debug(f"⏭️  Skipping {yaml_file.name} (already loaded, no changes)")
                    continue
                
                count = self._load_library_yaml_file(yaml_file, category)
                patterns_loaded += count
                self.loaded_files.add(file_key)
            
            if patterns_loaded > 0:
                stats[f"library-{category}"] = patterns_loaded
                logger.info(f"✅ Loaded knowledge-library/{category}: {patterns_loaded} patterns")
        
        return stats
    
    def _load_library_yaml_file(self, file_path: Path, category: str) -> int:
        """
        Load patterns from a knowledge-library YAML file.
        
        Args:
            file_path: Path to YAML file
            category: Category name (architecture, design-patterns, security)
        
        Returns:
            Number of patterns inserted/updated
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            if not isinstance(data, dict):
                logger.warning(f"Invalid YAML structure in {file_path.name}")
                return 0
            
            # Extract patterns using knowledge-library extraction strategies
            patterns = self._extract_library_patterns(data, file_path, category)
            
            # Store patterns in database
            patterns_loaded = 0
            with self.connection_manager.transaction() as conn:
                cursor = conn.cursor()
                
                for pattern in patterns:
                    # Check if pattern exists
                    cursor.execute(
                        "SELECT id FROM patterns WHERE pattern_id = ?",
                        (pattern['pattern_id'],)
                    )
                    existing = cursor.fetchone()
                    
                    if existing:
                        # Update existing pattern
                        cursor.execute("""
                            UPDATE patterns 
                            SET content = ?, confidence = ?, metadata = ?, 
                                last_accessed = ?
                            WHERE pattern_id = ?
                        """, (
                            pattern['content'],
                            pattern['confidence'],
                            pattern['metadata'],
                            datetime.now().isoformat(),
                            pattern['pattern_id']
                        ))
                    else:
                        # Insert new pattern
                        cursor.execute("""
                            INSERT INTO patterns (
                                pattern_id, title, content, pattern_type, confidence,
                                created_at, last_accessed, access_count, source,
                                metadata, is_pinned, scope, namespaces
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            pattern['pattern_id'],
                            pattern['title'],
                            pattern['content'],
                            pattern['pattern_type'],
                            pattern['confidence'],
                            pattern['created_at'],
                            pattern['last_accessed'],
                            pattern['access_count'],
                            pattern['source'],
                            pattern['metadata'],
                            pattern['is_pinned'],
                            pattern['scope'],
                            pattern['namespaces']
                        ))
                    
                    patterns_loaded += 1
                
                # Store file load metadata
                self._record_file_load(cursor, file_path)
            
            return patterns_loaded
        
        except Exception as e:
            logger.error(f"Failed to load {file_path.name}: {e}")
            return 0
    
    def _extract_library_patterns(
        self, 
        data: Dict[str, Any], 
        file_path: Path,
        category: str
    ) -> List[Dict[str, Any]]:
        """
        Extract patterns from knowledge-library YAML files.
        
        Handles the specific YAML structure used in knowledge-library:
        - csharp-patterns.yaml: creational_patterns, structural_patterns, behavioral_patterns
        - reactive-systems.yaml: architectural_patterns, kafka_integration, etc.
        - microservices-security.yaml: authentication_patterns, api_gateway_security, etc.
        - microservices-transition.yaml: strangler_application_pattern, database_decomposition, etc.
        
        Args:
            data: Parsed YAML data
            file_path: Source file path
            category: Category name
        
        Returns:
            List of pattern dictionaries
        """
        patterns = []
        metadata = data.get('metadata', {})
        file_stem = file_path.stem
        source_path = f"knowledge-library/{category}/{file_stem}.yaml"
        
        # Strategy 1: C# Design Patterns (creational/structural/behavioral)
        if 'creational_patterns' in data or 'structural_patterns' in data or 'behavioral_patterns' in data:
            patterns.extend(self._extract_csharp_patterns(data, file_stem, category, metadata, source_path))
        
        # Strategy 2: Architecture Patterns (reactive systems, microservices)
        architecture_keys = [
            'architectural_patterns', 'resiliency_principles', 'kafka_integration',
            'payout_flow_architecture', 'database_integration', 'idempotency_patterns'
        ]
        if any(key in data for key in architecture_keys):
            patterns.extend(self._extract_architecture_patterns(data, file_stem, category, metadata, source_path))
        
        # Strategy 3: Security Patterns (microservices security)
        security_keys = [
            'service_to_service_security', 'authentication_patterns', 'api_gateway_security',
            'rate_limiting', 'service_mesh_security', 'threat_modeling'
        ]
        if any(key in data for key in security_keys):
            patterns.extend(self._extract_microservices_security(data, file_stem, category, metadata, source_path))
        
        # Strategy 4: Migration Patterns (strangler, database decomposition)
        migration_keys = [
            'strangler_application_pattern', 'capability_identification', 'database_decomposition',
            'feature_toggles', 'routing_strategies', 'migration_anti_patterns'
        ]
        if any(key in data for key in migration_keys):
            patterns.extend(self._extract_migration_patterns(data, file_stem, category, metadata, source_path))
        
        # Strategy 5: Pattern Selection Guide (from knowledge-library design patterns)
        if 'pattern_selection_guide' in data:
            patterns.extend(self._extract_library_pattern_guide(data, file_stem, category, metadata, source_path))
        
        # Fallback: Generic extraction for any remaining top-level keys
        if not patterns:
            patterns.extend(self._extract_library_generic(data, file_stem, category, metadata, source_path))
        
        return patterns
    
    def _extract_csharp_patterns(
        self,
        data: Dict[str, Any],
        file_stem: str,
        category: str,
        metadata: Dict[str, Any],
        source_path: str
    ) -> List[Dict[str, Any]]:
        """Extract C# design patterns (creational/structural/behavioral categories)."""
        patterns = []
        
        pattern_categories = {
            'creational_patterns': 'creational',
            'structural_patterns': 'structural', 
            'behavioral_patterns': 'behavioral'
        }
        
        for yaml_key, pattern_type in pattern_categories.items():
            if yaml_key not in data:
                continue
            
            category_data = data[yaml_key]
            if not isinstance(category_data, dict):
                continue
            
            for pattern_name, pattern_data in category_data.items():
                if not isinstance(pattern_data, dict):
                    continue
                
                pattern_id = self._generate_pattern_id(f"csharp_{file_stem}", pattern_name)
                
                # Build rich content from pattern data
                content = {
                    'intent': pattern_data.get('intent', ''),
                    'category': pattern_data.get('category', pattern_type),
                    'when_to_use': pattern_data.get('when_to_use', []),
                    'participants': pattern_data.get('participants', []),
                    'csharp_implementation': pattern_data.get('csharp_implementation', {}),
                    'csharp_notes': pattern_data.get('csharp_notes', []),
                    'considerations': pattern_data.get('considerations', []),
                    'vs_other_patterns': pattern_data.get(f'vs_{pattern_name.lower()}', 
                                         pattern_data.get('comparison_with_factory_method', {}))
                }
                
                patterns.append({
                    'pattern_id': pattern_id,
                    'title': f"{pattern_name.replace('_', ' ').title()} Pattern (C#)",
                    'content': json.dumps(content),
                    'pattern_type': 'design_pattern',
                    'confidence': 1.0,
                    'created_at': datetime.now().isoformat(),
                    'last_accessed': datetime.now().isoformat(),
                    'access_count': 0,
                    'source': source_path,
                    'metadata': json.dumps(metadata),
                    'is_pinned': 1,
                    'scope': 'cortex',
                    'namespaces': json.dumps([category, "csharp", "design-patterns", pattern_type])
                })
        
        return patterns
    
    def _extract_architecture_patterns(
        self,
        data: Dict[str, Any],
        file_stem: str,
        category: str,
        metadata: Dict[str, Any],
        source_path: str
    ) -> List[Dict[str, Any]]:
        """Extract architecture patterns (reactive systems, microservices)."""
        patterns = []
        
        # Extract each top-level architecture section
        architecture_sections = [
            ('resiliency_principles', 'resiliency'),
            ('architectural_patterns', 'architecture'),
            ('kafka_integration', 'messaging'),
            ('payout_flow_architecture', 'workflow'),
            ('database_integration', 'data'),
            ('idempotency_patterns', 'resilience'),
            ('webclient_integration', 'integration'),
            ('dto_best_practices', 'patterns'),
            ('spring_boot_setup', 'framework')
        ]
        
        for section_key, pattern_subtype in architecture_sections:
            if section_key not in data:
                continue
            
            section_data = data[section_key]
            pattern_id = self._generate_pattern_id(f"arch_{file_stem}", section_key)
            
            patterns.append({
                'pattern_id': pattern_id,
                'title': section_key.replace('_', ' ').title(),
                'content': json.dumps(section_data),
                'pattern_type': 'architecture_pattern',
                'confidence': 1.0,
                'created_at': datetime.now().isoformat(),
                'last_accessed': datetime.now().isoformat(),
                'access_count': 0,
                'source': source_path,
                'metadata': json.dumps(metadata),
                'is_pinned': 1,
                'scope': 'cortex',
                'namespaces': json.dumps([category, "architecture", pattern_subtype, "microservices"])
            })
        
        return patterns
    
    def _extract_microservices_security(
        self,
        data: Dict[str, Any],
        file_stem: str,
        category: str,
        metadata: Dict[str, Any],
        source_path: str
    ) -> List[Dict[str, Any]]:
        """Extract microservices security patterns."""
        patterns = []
        
        security_sections = [
            ('service_to_service_security', 'transport'),
            ('authentication_patterns', 'authentication'),
            ('api_gateway_security', 'gateway'),
            ('rate_limiting', 'protection'),
            ('logging_and_monitoring', 'observability'),
            ('service_mesh_security', 'mesh'),
            ('security_testing', 'testing'),
            ('threat_modeling', 'analysis')
        ]
        
        for section_key, security_type in security_sections:
            if section_key not in data:
                continue
            
            section_data = data[section_key]
            pattern_id = self._generate_pattern_id(f"sec_{file_stem}", section_key)
            
            patterns.append({
                'pattern_id': pattern_id,
                'title': section_key.replace('_', ' ').title(),
                'content': json.dumps(section_data),
                'pattern_type': 'security_pattern',
                'confidence': 1.0,
                'created_at': datetime.now().isoformat(),
                'last_accessed': datetime.now().isoformat(),
                'access_count': 0,
                'source': source_path,
                'metadata': json.dumps(metadata),
                'is_pinned': 1,
                'scope': 'cortex',
                'namespaces': json.dumps([category, "security", security_type, "microservices"])
            })
        
        return patterns
    
    def _extract_migration_patterns(
        self,
        data: Dict[str, Any],
        file_stem: str,
        category: str,
        metadata: Dict[str, Any],
        source_path: str
    ) -> List[Dict[str, Any]]:
        """Extract microservices migration/transition patterns."""
        patterns = []
        
        migration_sections = [
            ('strangler_application_pattern', 'strangler'),
            ('capability_identification', 'analysis'),
            ('database_decomposition', 'database'),
            ('feature_toggles', 'deployment'),
            ('routing_strategies', 'routing'),
            ('api_versioning', 'api'),
            ('testing_strategies', 'testing'),
            ('migration_anti_patterns', 'anti-patterns'),
            ('organizational_considerations', 'organization')
        ]
        
        for section_key, migration_type in migration_sections:
            if section_key not in data:
                continue
            
            section_data = data[section_key]
            pattern_id = self._generate_pattern_id(f"mig_{file_stem}", section_key)
            
            patterns.append({
                'pattern_id': pattern_id,
                'title': section_key.replace('_', ' ').title(),
                'content': json.dumps(section_data),
                'pattern_type': 'migration_pattern',
                'confidence': 1.0,
                'created_at': datetime.now().isoformat(),
                'last_accessed': datetime.now().isoformat(),
                'access_count': 0,
                'source': source_path,
                'metadata': json.dumps(metadata),
                'is_pinned': 1,
                'scope': 'cortex',
                'namespaces': json.dumps([category, "migration", migration_type, "microservices"])
            })
        
        return patterns
    
    def _extract_library_pattern_guide(
        self,
        data: Dict[str, Any],
        file_stem: str,
        category: str,
        metadata: Dict[str, Any],
        source_path: str
    ) -> List[Dict[str, Any]]:
        """Extract pattern selection guide from knowledge-library."""
        patterns = []
        guide = data.get('pattern_selection_guide', {})
        
        for guide_type, guide_content in guide.items():
            pattern_id = self._generate_pattern_id(f"guide_{file_stem}", guide_type)
            
            patterns.append({
                'pattern_id': pattern_id,
                'title': f"Pattern Guide: {guide_type.replace('_', ' ').title()}",
                'content': json.dumps({guide_type: guide_content}),
                'pattern_type': 'pattern_guide',
                'confidence': 1.0,
                'created_at': datetime.now().isoformat(),
                'last_accessed': datetime.now().isoformat(),
                'access_count': 0,
                'source': source_path,
                'metadata': json.dumps(metadata),
                'is_pinned': 1,
                'scope': 'cortex',
                'namespaces': json.dumps([category, "pattern-guide"])
            })
        
        return patterns
    
    def _extract_library_generic(
        self,
        data: Dict[str, Any],
        file_stem: str,
        category: str,
        metadata: Dict[str, Any],
        source_path: str
    ) -> List[Dict[str, Any]]:
        """Generic extraction for knowledge-library YAML files."""
        patterns = []
        
        for key, value in data.items():
            if key == 'metadata':
                continue
            
            if not isinstance(value, (dict, list)):
                continue
            
            pattern_id = self._generate_pattern_id(f"lib_{file_stem}", key)
            
            patterns.append({
                'pattern_id': pattern_id,
                'title': key.replace('_', ' ').title(),
                'content': json.dumps(value),
                'pattern_type': category,
                'confidence': 0.9,
                'created_at': datetime.now().isoformat(),
                'last_accessed': datetime.now().isoformat(),
                'access_count': 0,
                'source': source_path,
                'metadata': json.dumps(metadata),
                'is_pinned': 1,
                'scope': 'cortex',
                'namespaces': json.dumps([category, "knowledge-library"])
            })
        
        return patterns
    
    def _generate_pattern_id(self, file_stem: str, pattern_name: str) -> str:
        """Generate unique pattern ID from file and pattern name."""
        # Use hash to keep IDs consistent across reloads
        source_str = f"{file_stem}:{pattern_name}"
        hash_suffix = hashlib.md5(source_str.encode()).hexdigest()[:8]
        safe_name = pattern_name.lower().replace(' ', '_').replace('-', '_')
        safe_name = ''.join(c for c in safe_name if c.isalnum() or c == '_')
        return f"kb_{file_stem}_{safe_name}_{hash_suffix}"
    
    def _is_file_loaded(self, file_path: Path) -> bool:
        """Check if file has been loaded and hasn't changed since."""
        with self.connection_manager.transaction() as conn:
            cursor = conn.cursor()
            
            # Check if file_loads table exists
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='file_loads'
            """)
            
            if not cursor.fetchone():
                self._create_file_loads_table(cursor)
                return False
            
            # Get file modification time
            file_mtime = file_path.stat().st_mtime
            file_hash = self._calculate_file_hash(file_path)
            
            cursor.execute("""
                SELECT file_hash, load_timestamp 
                FROM file_loads 
                WHERE file_path = ?
            """, (str(file_path),))
            
            result = cursor.fetchone()
            if not result:
                return False
            
            stored_hash, _ = result
            return stored_hash == file_hash
    
    def _record_file_load(self, cursor, file_path: Path):
        """Record file load with hash and timestamp."""
        # Ensure table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='file_loads'
        """)
        
        if not cursor.fetchone():
            self._create_file_loads_table(cursor)
        
        file_hash = self._calculate_file_hash(file_path)
        
        cursor.execute("""
            INSERT OR REPLACE INTO file_loads 
            (file_path, file_hash, load_timestamp)
            VALUES (?, ?, ?)
        """, (str(file_path), file_hash, datetime.now().isoformat()))
    
    def _create_file_loads_table(self, cursor):
        """Create file_loads tracking table."""
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS file_loads (
                file_path TEXT PRIMARY KEY,
                file_hash TEXT NOT NULL,
                load_timestamp TEXT NOT NULL
            )
        """)
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate MD5 hash of file content."""
        hasher = hashlib.md5()
        with open(file_path, 'rb') as f:
            hasher.update(f.read())
        return hasher.hexdigest()
    
    def get_load_stats(self) -> Dict[str, Any]:
        """Get statistics about loaded knowledge files."""
        with self.connection_manager.transaction() as conn:
            cursor = conn.cursor()
            
            # Check if file_loads table exists
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='file_loads'
            """)
            
            if not cursor.fetchone():
                return {
                    'files_loaded': 0,
                    'patterns_from_knowledge': 0,
                    'patterns_from_library': 0,
                    'last_load': None
                }
            
            cursor.execute("SELECT COUNT(*) FROM file_loads")
            files_loaded = cursor.fetchone()[0]
            
            cursor.execute("""
                SELECT COUNT(*) FROM patterns 
                WHERE source LIKE 'knowledge/%'
            """)
            patterns_count = cursor.fetchone()[0]
            
            cursor.execute("""
                SELECT COUNT(*) FROM patterns 
                WHERE source LIKE 'knowledge-library/%'
            """)
            library_patterns_count = cursor.fetchone()[0]
            
            cursor.execute("""
                SELECT MAX(load_timestamp) FROM file_loads
            """)
            last_load = cursor.fetchone()[0]
            
            return {
                'files_loaded': files_loaded,
                'patterns_from_knowledge': patterns_count,
                'patterns_from_library': library_patterns_count,
                'last_load': last_load
            }
