"""Domain Brain models - Re-export from cortex_brain.domain_brain.models."""

from cortex_brain.domain_brain.models import *  # noqa
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import uuid4
import hashlib


class DomainBrainAPI:
    """Domain Brain API - Query and manage domain knowledge."""
    
    def __init__(self):
        """Initialize Domain Brain API."""
        self._domains: Dict[str, Any] = {}
        self._audit_log: List[Dict[str, Any]] = []
    
    def upsert_domain(self, domain: Any) -> None:
        """Upsert a domain.
        
        Args:
            domain: Domain to upsert.
            
        Raises:
            ValueError: If domain has circular dependencies.
        """
        # Check for circular dependencies
        if hasattr(domain, 'entities'):
            self._check_circular_dependencies(domain)
        self._domains[domain.domain_id] = domain
        self._audit_log.append({
            "operation": "CREATE",
            "domain_id": domain.domain_id,
            "timestamp": datetime.now(),
        })
    
    def _check_circular_dependencies(self, domain: Any) -> None:
        """Check for circular dependencies in domain entities.
        
        Args:
            domain: Domain to check.
            
        Raises:
            ValueError: If circular dependency detected.
        """
        visited = set()
        rec_stack = set()
        
        def has_cycle(entity_id: str, entities: Dict[str, Any]) -> bool:
            visited.add(entity_id)
            rec_stack.add(entity_id)
            
            entity = entities.get(entity_id)
            if entity and hasattr(entity, 'metadata') and entity.metadata:
                depends_on = entity.metadata.get("depends_on", [])
                for dep in depends_on:
                    if dep not in visited:
                        if has_cycle(dep, entities):
                            return True
                    elif dep in rec_stack:
                        return True
            
            rec_stack.remove(entity_id)
            return False
        
        for entity_id in domain.entities:
            if entity_id not in visited:
                if has_cycle(entity_id, domain.entities):
                    raise ValueError(f"Circular dependency detected in domain {domain.domain_id}")
    
    def query_domain(self, domain_id: str) -> Optional[Any]:
        """Query a domain by ID.
        
        Args:
            domain_id: Domain ID.
            
        Returns:
            Domain if found, None otherwise.
        """
        return self._domains.get(domain_id)
    
    def list_domains(self) -> List[Any]:
        """List all domains.
        
        Returns:
            List of domains.
        """
        return list(self._domains.values())
    
    def search_entities(self, query: str) -> List[Any]:
        """Search entities across all domains.
        
        Args:
            query: Search query.
            
        Returns:
            List of matching entities.
        """
        results = []
        for domain in self._domains.values():
            for entity in domain.entities.values():
                if query.lower() in entity.name.lower() or query.lower() in entity.description.lower():
                    results.append(entity)
        return results
    
    def delete_domain(self, domain_id: str) -> bool:
        """Delete a domain.
        
        Args:
            domain_id: Domain ID.
            
        Returns:
            True if deleted, False if not found.
        """
        if domain_id in self._domains:
            del self._domains[domain_id]
            self._audit_log.append({
                "operation": "DELETE",
                "domain_id": domain_id,
                "timestamp": datetime.now(),
            })
            return True
        return False
    
    def get_conflicts(self, domain_id: str) -> List[Any]:
        """Get conflicts for a domain.
        
        Args:
            domain_id: Domain ID.
            
        Returns:
            List of conflicts.
        """
        domain = self.query_domain(domain_id)
        if not domain:
            return []
        return domain.conflicts if hasattr(domain, 'conflicts') else []
    
    def add_conflict(self, domain_id: str, conflict: Any) -> None:
        """Add a conflict to a domain.
        
        Args:
            domain_id: Domain ID.
            conflict: Conflict to add.
        """
        domain = self.query_domain(domain_id)
        if domain:
            if not hasattr(domain, 'conflicts'):
                domain.conflicts = []
            domain.conflicts.append(conflict)
    
    def resolve_conflict(self, conflict_id: str, domain_id: str, resolved_value: str, resolution_method: str = "") -> bool:
        """Resolve a conflict.
        
        Args:
            conflict_id: Conflict ID.
            domain_id: Domain ID.
            resolved_value: Resolved value.
            resolution_method: Resolution strategy (optional).
            
        Returns:
            True if resolved, False if not found.
        """
        domain = self.query_domain(domain_id)
        if not domain or not hasattr(domain, 'conflicts'):
            return False
        for conflict in domain.conflicts:
            if conflict.conflict_id == conflict_id:
                conflict.resolution = resolved_value
                if resolution_method:
                    conflict.resolution_method = resolution_method
                conflict.resolved_at = datetime.now()
                return True
        return False
    
    def validate_domain(self, domain: Any) -> Any:
        """Validate a domain.
        
        Args:
            domain: Domain to validate.
            
        Returns:
            ValidationResult object with validation status.
        """
        from cortex_brain.domain_brain.models import ValidationResult
        
        errors = []
        conflicts_detected = []
        
        # Check for conflicts between entities
        if hasattr(domain, 'entities'):
            entity_names = {}
            for entity_id, entity in domain.entities.items():
                name = entity.name
                if name in entity_names:
                    # Found duplicate name
                    conflicts_detected.append({
                        "type": "duplicate_name",
                        "entity1": entity_names[name],
                        "entity2": entity_id,
                        "name": name
                    })
                else:
                    entity_names[name] = entity_id
        
        # Check for explicit conflicts
        if hasattr(domain, 'conflicts') and domain.conflicts:
            conflicts_detected.extend(domain.conflicts)
        
        is_valid = len(errors) == 0
        return ValidationResult(
            is_valid=is_valid,
            errors=errors,
            conflicts_detected=conflicts_detected
        )
    
    def audit_domain(self, domain_id: str) -> List[Dict[str, Any]]:
        """Get audit trail for a domain.
        
        Args:
            domain_id: Domain ID.
            
        Returns:
            List of audit entries for the domain.
        """
        return [entry for entry in self._audit_log if entry.get("domain_id") == domain_id]
    
    def get_audit_stats(self) -> Dict[str, Any]:
        """Get audit statistics.
        
        Returns:
            Dictionary with audit stats.
        """
        return {
            "cache_size": len(self._domains),
            "total_entries": len(self._audit_log),
            "domains_count": len(self._domains),
        }


class ConsistencyValidator:
    """Validate domain consistency and referential integrity."""
    
    def validate_domain(self, domain: Any) -> Any:
        """Validate domain for consistency.
        
        Args:
            domain: Domain to validate.
            
        Returns:
            ValidationResult with validation status and errors.
        """
        from cortex_brain.domain_brain.models import ValidationResult
        
        errors = []
        conflicts_detected = []
        
        if not hasattr(domain, 'entities'):
            return ValidationResult(is_valid=True, errors=[], conflicts_detected=[])
        
        entities = domain.entities
        entity_names = {}
        
        # Check for circular dependencies and referential integrity
        for entity_id, entity in entities.items():
            # Track duplicate names from different sources
            entity_key = (entity.name, entity.source if hasattr(entity, 'source') else 'unknown')
            if entity.name in entity_names and entity_names[entity.name].get('source') != entity.source:
                conflicts_detected.append({
                    "type": "duplicate_name_different_source",
                    "entity1": entity_names[entity.name]['id'],
                    "entity2": entity_id,
                    "name": entity.name,
                })
            if entity.name not in entity_names:
                entity_names[entity.name] = {'id': entity_id, 'source': entity.source if hasattr(entity, 'source') else 'unknown'}
            
            # Check references
            if hasattr(entity, 'metadata') and entity.metadata:
                references = entity.metadata.get('references', [])
                for ref in references:
                    if ref not in entities:
                        errors.append(f"Entity {entity_id} references non-existent entity: {ref}")
                
                # Check dependencies
                depends_on = entity.metadata.get('depends_on', [])
                for dep in depends_on:
                    if dep not in entities:
                        errors.append(f"Entity {entity_id} depends on non-existent entity: {dep}")
        
        # Check for circular dependencies
        circular_errors = self._detect_circular_dependencies(entities)
        errors.extend(circular_errors)
        
        is_valid = len(errors) == 0
        return ValidationResult(
            is_valid=is_valid,
            errors=errors,
            conflicts_detected=conflicts_detected
        )
    
    def validate_entity(self, entity: Any, domain: Any) -> Any:
        """Validate a single entity within a domain.
        
        Args:
            entity: Entity to validate.
            domain: Parent domain for context.
            
        Returns:
            ValidationResult with validation status.
        """
        from cortex_brain.domain_brain.models import ValidationResult
        
        errors = []
        
        if not hasattr(domain, 'entities'):
            return ValidationResult(is_valid=True, errors=[], conflicts_detected=[])
        
        entities = domain.entities
        
        # Check references
        if hasattr(entity, 'metadata') and entity.metadata:
            references = entity.metadata.get('references', [])
            for ref in references:
                if ref not in entities:
                    errors.append(f"Entity references non-existent entity: {ref}")
            
            # Check dependencies
            depends_on = entity.metadata.get('depends_on', [])
            for dep in depends_on:
                if dep not in entities:
                    errors.append(f"Entity depends on non-existent entity: {dep}")
        
        is_valid = len(errors) == 0
        return ValidationResult(
            is_valid=is_valid,
            errors=errors,
            conflicts_detected=[]
        )
    
    def _detect_circular_dependencies(self, entities: Dict[str, Any]) -> List[str]:
        """Detect circular dependencies in entities.
        
        Args:
            entities: Dictionary of entities to check.
            
        Returns:
            List of error messages for circular dependencies.
        """
        errors = []
        visited = set()
        rec_stack = set()
        
        def has_cycle(entity_id: str) -> bool:
            visited.add(entity_id)
            rec_stack.add(entity_id)
            
            entity = entities.get(entity_id)
            if entity and hasattr(entity, 'metadata') and entity.metadata:
                depends_on = entity.metadata.get('depends_on', [])
                for dep in depends_on:
                    if dep in entities:
                        if dep not in visited:
                            if has_cycle(dep):
                                return True
                        elif dep in rec_stack:
                            errors.append(f"Circular dependency detected involving entity {entity_id}")
                            return True
            
            rec_stack.remove(entity_id)
            return False
        
        for entity_id in entities:
            if entity_id not in visited:
                has_cycle(entity_id)
        
        return errors


class AuditLogger:
    """Audit logger for domain operations with hash chain integrity."""
    
    def __init__(self):
        """Initialize audit logger."""
        self._log: List[Any] = []
        self._cache: Dict[str, Any] = {}
        self._last_hash = ""
    
    def log_operation(
        self,
        operation: Any,
        domain_id: Optional[str] = None,
        entity_id: Optional[str] = None,
        description: str = "",
        previous_value: Optional[Dict[str, Any]] = None,
        new_value: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Log an audit operation.
        
        Args:
            operation: AuditOperationType for the operation.
            domain_id: Associated domain ID.
            entity_id: Associated entity ID.
            description: Human-readable description.
            previous_value: Previous value before update.
            new_value: New value after update.
            
        Returns:
            AuditEntry with hash and other details.
        """
        from cortex_brain.domain_brain.models import AuditEntry
        
        entry_id = str(uuid4())
        
        # Create hash for this entry
        hash_input = f"{entry_id}{operation}{domain_id}{entity_id}{str(datetime.now())}"
        entry_hash = hashlib.sha256(hash_input.encode()).hexdigest()
        
        # Create audit entry
        entry = AuditEntry(
            entry_id=entry_id,
            operation=operation,
            domain_id=domain_id,
            entity_id=entity_id,
            hash=entry_hash,
            previous_hash=self._last_hash,
            description=description,
            previous_value=previous_value,
            new_value=new_value,
        )
        
        # Append to log and cache
        self._log.append(entry)
        self._cache[entry_id] = entry
        self._last_hash = entry_hash
        
        return entry
    
    def get_entry(self, entry_id: str) -> Optional[Any]:
        """Get an audit entry by ID.
        
        Args:
            entry_id: Entry ID to retrieve.
            
        Returns:
            AuditEntry if found, None otherwise.
        """
        return self._cache.get(entry_id)
    
    def get_all_entries(self) -> List[Any]:
        """Get all audit entries.
        
        Returns:
            List of all audit entries in order.
        """
        return self._log.copy()
    
    def get_entry_count(self) -> int:
        """Get total number of audit entries.
        
        Returns:
            Number of audit entries.
        """
        return len(self._log)
    
    def get_recent_entries(self, limit: int = 10) -> List[Any]:
        """Get recent audit entries.
        
        Args:
            limit: Maximum number of entries to return.
            
        Returns:
            List of recent audit entries.
        """
        return self._log[-limit:] if limit > 0 else []
    
    def get_domain_audit_trail(self, domain_id: str) -> List[Any]:
        """Get audit trail for a specific domain.
        
        Args:
            domain_id: Domain ID to filter by.
            
        Returns:
            List of audit entries for the domain.
        """
        return [entry for entry in self._log if entry.domain_id == domain_id]
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics.
        
        Returns:
            Dictionary with cache stats.
        """
        return {
            "cache_size": len(self._cache),
            "total_entries": len(self._log),
        }
    
    def verify_hash_chain(self) -> bool:
        """Verify the integrity of the hash chain.
        
        Returns:
            True if hash chain is valid, False otherwise.
        """
        if not self._log:
            return True
        
        for i, entry in enumerate(self._log):
            if i == 0:
                if entry.previous_hash != "":
                    return False
            else:
                prev_entry = self._log[i - 1]
                if entry.previous_hash != prev_entry.hash:
                    return False
        
        return True


__all__ = ["DomainBrainAPI", "ConsistencyValidator", "AuditLogger"]
