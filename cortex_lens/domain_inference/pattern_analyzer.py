"""
Domain Pattern Analyzer

Detects domain patterns, clusters entities, and identifies bounded contexts.

Author: CORTEX Architect
Phase: Phase 66 S3
"""

import logging
import re
from typing import List, Dict, Set, Any, Optional
from pathlib import Path
from collections import defaultdict, Counter

logger = logging.getLogger(__name__)


class PatternAnalyzer:
    """
    Analyzes code structure to detect domain patterns and bounded contexts.
    
    Capabilities:
    - Domain clustering by naming patterns
    - Aggregate root detection (DDD)
    - Repository/Service pattern identification
    - Bounded context boundary detection
    - Coupling analysis between domains
    
    Example:
        analyzer = PatternAnalyzer()
        
        # Cluster classes by domain prefix
        clusters = analyzer.cluster_by_prefix(
            ["UserRepository", "UserService", "OrderRepository"],
            min_cluster_size=2
        )
        # Returns: {"User": ["UserRepository", "UserService"], "Order": [...]}
        
        # Detect aggregate root
        root = analyzer.detect_aggregate_root(user_cluster)
        # Returns: "User" (the entity class)
    """
    
    def __init__(self, storage=None):
        """
        Initialize pattern analyzer.
        
        Args:
            storage: Optional GraphStorage instance for graph-based analysis
        """
        self.storage = storage
        self.pattern_keywords = {
            "repository": ["Repository", "Repo", "Store", "DAO"],
            "service": ["Service", "Manager", "Handler", "Processor"],
            "validator": ["Validator", "Validation", "Checker"],
            "factory": ["Factory", "Builder", "Creator"],
            "entity": ["Entity", "Model", "Domain"]
        }
        logger.debug("Initialized PatternAnalyzer")
    
    def cluster_by_prefix(
        self, 
        names: List[str], 
        min_cluster_size: int = 2
    ) -> Dict[str, List[str]]:
        """
        Cluster names by shared prefixes (domain clustering).
        
        Args:
            names: List of class/module names
            min_cluster_size: Minimum cluster size to return
        
        Returns:
            Dictionary mapping prefix to list of names
        
        Example:
            Input: ["UserRepository", "UserService", "OrderRepo"]
            Output: {"User": ["UserRepository", "UserService"], "Order": ["OrderRepo"]}
        """
        logger.debug(f"Clustering {len(names)} names by prefix")
        
        # Extract potential prefixes (uppercase word boundaries)
        clusters: Dict[str, List[str]] = defaultdict(list)
        
        for name in names:
            # Find all uppercase word starts (e.g., "UserRepository" → ["User", "Repository"])
            words = re.findall(r'[A-Z][a-z]*', name)
            
            if len(words) >= 2:
                # First word is likely the domain prefix
                prefix = words[0]
                clusters[prefix].append(name)
        
        # Filter by minimum cluster size
        filtered = {
            prefix: members 
            for prefix, members in clusters.items() 
            if len(members) >= min_cluster_size
        }
        
        logger.debug(f"Found {len(filtered)} clusters")
        return dict(filtered)
    
    def detect_aggregate_root(self, cluster: Dict[str, Any]) -> Optional[str]:
        """
        Detect aggregate root in a domain cluster (DDD pattern).
        
        Aggregate root is typically:
        - The entity class without suffixes (User vs UserRepository)
        - Has lifecycle methods (__init__, save, etc.)
        - Referenced by repository/service classes
        
        Args:
            cluster: Dictionary mapping class name to metadata
        
        Returns:
            Name of aggregate root, or None if not detected
        
        Example:
            cluster = {
                "User": {"type": "entity", "methods": ["__init__", "update"]},
                "UserRepository": {"type": "repository", "methods": ["save"]}
            }
            Returns: "User"
        """
        logger.debug(f"Detecting aggregate root in cluster of {len(cluster)} classes")
        
        # Score each candidate
        scores: Dict[str, float] = {}
        
        for name, metadata in cluster.items():
            score = 0.0
            
            # Highest score: entity with no suffix
            if metadata.get("type") == "entity":
                score += 3.0
            
            # Shorter names more likely (User vs UserRepository)
            if not any(suffix in name for suffix in ["Repository", "Service", "Validator", "Factory"]):
                score += 2.0
            
            # Has lifecycle methods
            methods = metadata.get("methods", [])
            if "__init__" in methods:
                score += 1.0
            if any(m in methods for m in ["save", "update", "delete"]):
                score += 0.5
            
            scores[name] = score
        
        if not scores:
            return None
        
        # Return highest scoring class
        aggregate_root = max(scores.items(), key=lambda x: x[1])[0]
        logger.debug(f"Detected aggregate root: {aggregate_root}")
        return aggregate_root
    
    def detect_pattern(
        self, 
        pattern_name: str, 
        classes: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Detect architectural pattern in class list.
        
        Args:
            pattern_name: Pattern to detect (repository, service, validator, etc.)
            classes: List of class metadata dictionaries
        
        Returns:
            List of classes matching the pattern
        
        Example:
            classes = [
                {"name": "UserRepository", "methods": ["save", "find"]},
                {"name": "UserService", "methods": ["create_user"]}
            ]
            detect_pattern("repository", classes)
            # Returns: [{"name": "UserRepository", ...}]
        """
        logger.debug(f"Detecting '{pattern_name}' pattern in {len(classes)} classes")
        
        if pattern_name not in self.pattern_keywords:
            logger.warning(f"Unknown pattern: {pattern_name}")
            return []
        
        keywords = self.pattern_keywords[pattern_name]
        matches = []
        
        for cls in classes:
            name = cls.get("name", "")
            
            # Check if name contains pattern keyword
            if any(keyword in name for keyword in keywords):
                matches.append(cls)
                continue
            
            # Check if inherits from pattern base class
            bases = cls.get("bases", [])
            if any(keyword in base for base in bases for keyword in keywords):
                matches.append(cls)
        
        logger.debug(f"Found {len(matches)} {pattern_name} classes")
        return matches
    
    def detect_bounded_contexts(
        self, 
        modules: Dict[str, List[str]]
    ) -> List[Dict[str, Any]]:
        """
        Detect bounded contexts from module structure.
        
        Bounded context indicators:
        - Self-contained module with multiple patterns (repo + service + validator)
        - Cohesive naming (all classes share prefix)
        - Minimal cross-module dependencies
        
        Args:
            modules: Dictionary mapping module name to class names
        
        Returns:
            List of bounded context descriptors
        
        Example:
            modules = {
                "user": ["UserRepository", "UserService"],
                "order": ["OrderRepository", "OrderService"],
                "shared": ["BaseRepository"]
            }
            Returns: [
                {"name": "user", "classes": [...], "confidence": 0.9},
                {"name": "order", "classes": [...], "confidence": 0.9}
            ]
        """
        logger.debug(f"Detecting bounded contexts in {len(modules)} modules")
        
        contexts = []
        
        for module_name, class_names in modules.items():
            # Skip shared/common modules
            if module_name.lower() in ["shared", "common", "utils", "base"]:
                continue
            
            # Skip if too few classes
            if len(class_names) < 2:
                continue
            
            # Check for cohesive naming
            clusters = self.cluster_by_prefix(class_names, min_cluster_size=1)
            has_cohesion = len(clusters) <= 2  # Max 2 prefixes indicates cohesion
            
            # Check for multiple patterns
            pattern_count = 0
            for pattern in ["repository", "service", "validator"]:
                if any(kw in " ".join(class_names) for kw in self.pattern_keywords[pattern]):
                    pattern_count += 1
            
            # Calculate confidence
            confidence = 0.0
            if has_cohesion:
                confidence += 0.4
            confidence += min(pattern_count * 0.3, 0.6)  # Max 0.6 for patterns
            
            if confidence >= 0.5:
                contexts.append({
                    "name": module_name,
                    "classes": class_names,
                    "pattern_count": pattern_count,
                    "confidence": confidence
                })
        
        logger.debug(f"Detected {len(contexts)} bounded contexts")
        return contexts
    
    def analyze_naming_conventions(
        self, 
        names: List[str]
    ) -> Dict[str, Any]:
        """
        Analyze naming conventions in codebase.
        
        Args:
            names: List of class/function names
        
        Returns:
            Dictionary with convention analysis
        
        Example:
            names = ["UserRepository", "user_service", "USER_CONST"]
            Returns: {
                "primary_style": "PascalCase",
                "styles": {"PascalCase": 1, "snake_case": 1, "SCREAMING_CASE": 1},
                "consistency_score": 0.33
            }
        """
        logger.debug(f"Analyzing naming conventions for {len(names)} names")
        
        styles = Counter()
        
        for name in names:
            if re.match(r'^[A-Z][a-z]+(?:[A-Z][a-z]+)*$', name):
                styles["PascalCase"] += 1
            elif re.match(r'^[a-z]+(?:_[a-z]+)*$', name):
                styles["snake_case"] += 1
            elif re.match(r'^[A-Z]+(?:_[A-Z]+)*$', name):
                styles["SCREAMING_CASE"] += 1
            elif re.match(r'^[a-z]+(?:[A-Z][a-z]+)*$', name):
                styles["camelCase"] += 1
        
        total = sum(styles.values())
        primary_style = styles.most_common(1)[0][0] if styles else "Unknown"
        consistency_score = styles[primary_style] / total if total > 0 else 0.0
        
        result = {
            "primary_style": primary_style,
            "styles": dict(styles),
            "consistency_score": consistency_score
        }
        
        logger.debug(f"Primary style: {primary_style} (consistency: {consistency_score:.2f})")
        return result
    
    def analyze_coupling(
        self, 
        imports: Dict[str, List[str]], 
        clusters: Dict[str, List[str]]
    ) -> Dict[str, Any]:
        """
        Analyze coupling between domain clusters.
        
        Args:
            imports: Dictionary mapping class to its imports
            clusters: Dictionary mapping domain prefix to class list
        
        Returns:
            Coupling analysis with cross-domain dependencies
        
        Example:
            imports = {"OrderService": ["UserService", "OrderRepository"]}
            clusters = {"User": ["UserService"], "Order": ["OrderService", "OrderRepository"]}
            Returns: {
                "cross_domain": [{"from": "Order", "to": "User", "strength": 1}],
                "internal": {...}
            }
        """
        logger.debug(f"Analyzing coupling for {len(clusters)} clusters")
        
        # Build reverse mapping: class → domain
        class_to_domain = {}
        for domain, classes in clusters.items():
            for cls in classes:
                class_to_domain[cls] = domain
        
        # Detect cross-domain dependencies
        cross_domain: List[Dict[str, Any]] = []
        internal_deps = defaultdict(int)
        
        for cls, imported_classes in imports.items():
            cls_domain = class_to_domain.get(cls)
            if not cls_domain:
                continue
            
            for imported_cls in imported_classes:
                imported_domain = class_to_domain.get(imported_cls)
                if not imported_domain:
                    continue
                
                if cls_domain == imported_domain:
                    # Internal dependency
                    internal_deps[cls_domain] += 1
                else:
                    # Cross-domain dependency
                    cross_domain.append({
                        "from": cls_domain,
                        "to": imported_domain,
                        "via": f"{cls} → {imported_cls}",
                        "strength": 1
                    })
        
        logger.debug(f"Found {len(cross_domain)} cross-domain dependencies")
        return {
            "cross_domain": cross_domain,
            "internal": dict(internal_deps)
        }
    
    def calculate_confidence(self, signals: Dict[str, Any]) -> float:
        """
        Calculate confidence score for domain inference.
        
        Weighted combination of signals:
        - Prefix match count: 0.2 per match (max 0.4)
        - Has repository: 0.2
        - Has service: 0.2
        - Has validator: 0.1
        - Naming consistency: 0.1
        
        Args:
            signals: Dictionary of detection signals
        
        Returns:
            Confidence score in [0.0, 1.0]
        
        Example:
            signals = {
                "prefix_match_count": 4,
                "has_repository": True,
                "has_service": True,
                "naming_consistency": 0.9
            }
            Returns: ~0.85
        """
        score = 0.0
        
        # Prefix clustering strength
        prefix_count = signals.get("prefix_match_count", 0)
        score += min(prefix_count * 0.1, 0.4)
        
        # Pattern presence
        if signals.get("has_repository"):
            score += 0.2
        if signals.get("has_service"):
            score += 0.2
        if signals.get("has_validator"):
            score += 0.1
        
        # Naming consistency
        naming_consistency = signals.get("naming_consistency", 0.0)
        score += naming_consistency * 0.1
        
        # Clamp to [0.0, 1.0]
        confidence = max(0.0, min(1.0, score))
        
        logger.debug(f"Calculated confidence: {confidence:.2f}")
        return confidence
    
    def analyze_directory(self, directory: Path) -> List[Dict[str, Any]]:
        """
        Analyze directory structure to detect domains.
        
        Args:
            directory: Path to directory to analyze
        
        Returns:
            List of detected domains with metadata
        
        Example:
            domains = analyzer.analyze_directory(Path("cortex/"))
            # Returns: [{"name": "orchestrator", "classes": [...], ...}]
        """
        logger.info(f"Analyzing directory: {directory}")
        
        # Walk directory to collect Python files
        modules: Dict[str, List[str]] = defaultdict(list)
        
        for py_file in directory.rglob("*.py"):
            if "__pycache__" in str(py_file) or "test" in str(py_file):
                continue
            
            # Get module name from path
            relative = py_file.relative_to(directory)
            module_name = relative.parts[0] if len(relative.parts) > 1 else relative.stem
            
            # Extract class names (simple regex, not full AST)
            content = py_file.read_text(encoding="utf-8")
            class_names = re.findall(r'^class\s+([A-Z]\w+)', content, re.MULTILINE)
            
            modules[module_name].extend(class_names)
        
        # Detect bounded contexts
        contexts = self.detect_bounded_contexts(modules)
        
        logger.info(f"Detected {len(contexts)} domains in {directory}")
        return contexts
    
    def analyze_domains(self) -> List[Dict[str, Any]]:
        """
        Analyze knowledge graph to detect and cluster domains.
        
        Requires storage to be initialized with graph data.
        
        Returns:
            List of detected domains with:
            - name: Domain name
            - entities: List of entity class names
            - patterns: Detected patterns (repository, service, etc.)
            - confidence: Confidence score (0.0-1.0)
        
        Example:
            storage = GraphStorage("graph.db")
            analyzer = PatternAnalyzer(storage)
            domains = analyzer.analyze_domains()
            # Returns: [
            #     {"name": "User", "entities": ["User", "UserRepository", ...], "confidence": 0.85},
            #     {"name": "Order", "entities": ["Order", "OrderService", ...], "confidence": 0.92}
            # ]
        """
        if not self.storage:
            raise ValueError("Storage not initialized. Pass GraphStorage to constructor.")
        
        logger.info("Analyzing domains from knowledge graph")
        
        # Get all class nodes from graph
        from cortex_lens.knowledge_graph.graph_query import GraphQuery
        query = GraphQuery(self.storage)
        
        # Get statistics to understand graph structure
        stats = self.storage.get_statistics()
        logger.debug(f"Graph stats: {stats}")
        
        # Query all Class nodes
        conn = self.storage._get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT name FROM nodes WHERE node_type = 'Class'
        """)
        
        class_names = [row["name"] for row in cursor.fetchall()]
        logger.debug(f"Found {len(class_names)} classes in graph")
        
        if not class_names:
            logger.warning("No classes found in graph")
            return []
        
        # Cluster classes by domain prefix
        clusters = self.cluster_by_prefix(class_names, min_cluster_size=1)
        
        # Build domain objects with patterns and confidence
        domains = []
        for domain_name, entities in clusters.items():
            # Detect patterns in entities by checking name suffixes
            patterns_detected = {}
            for entity in entities:
                # Check each pattern keyword
                for pattern_type, keywords in self.pattern_keywords.items():
                    if any(keyword in entity for keyword in keywords):
                        patterns_detected[pattern_type] = patterns_detected.get(pattern_type, 0) + 1
                        break  # Only count each entity once
            
            # Calculate confidence based on:
            # - Number of entities (more = higher confidence)
            # - Pattern diversity (repository + service = higher)
            # - Naming consistency
            confidence_signals = {
                "entity_count": len(entities),
                "pattern_diversity": len(patterns_detected),
                "has_repository": "repository" in patterns_detected,
                "has_service": "service" in patterns_detected
            }
            confidence = self.calculate_confidence(confidence_signals)
            
            domains.append({
                "name": domain_name,
                "entities": entities,
                "patterns": patterns_detected,
                "confidence": confidence
            })
        
        # Sort by confidence (highest first)
        domains.sort(key=lambda d: d["confidence"], reverse=True)
        
        logger.info(f"Detected {len(domains)} domains from graph")
        for domain in domains:
            logger.debug(f"  - {domain['name']}: {len(domain['entities'])} entities, confidence={domain['confidence']:.2f}")
        
        return domains

