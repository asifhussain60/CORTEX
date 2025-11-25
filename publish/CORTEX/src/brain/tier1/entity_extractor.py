"""
CORTEX Brain - Tier 1: EntityExtractor

Purpose: Extract entities from conversation messages and link to conversations

Features:
- Extract file paths, features, components, services from messages
- Link entities to conversations for quick lookups
- Support fuzzy matching for entity resolution
- Track entity usage frequency
- Enable "Make it purple" style references

Entity Types:
- Files: Source files mentioned in conversation
- Features: Features being implemented/discussed
- Components: UI components, services, modules
- Concepts: Abstract concepts (dark mode, authentication, etc.)

Author: CORTEX Development Team
Version: 1.0.0
"""

import re
from typing import List, Dict, Any, Set, Optional
from pathlib import Path


class EntityExtractor:
    """
    Extracts and manages entities from conversation messages.
    
    Supports multiple entity types and provides fuzzy matching
    for resolving ambiguous references.
    """
    
    # Entity extraction patterns
    FILE_PATTERNS = [
        r'`([^`]+\.(py|md|ts|tsx|js|jsx|cs|razor|css|scss|yaml|json|xml|html))`',  # Backticked files
        r'([A-Z][a-zA-Z0-9_-]*\.(py|md|ts|tsx|js|jsx|cs|razor|css|scss|yaml|json|xml|html))',  # CamelCase files
        r'([a-z][a-z0-9_-]*\.(py|md|ts|tsx|js|jsx|cs|razor|css|scss|yaml|json|xml|html))',  # lowercase files
        r'([a-z][a-z0-9_/-]*/(src|tests?|components?|services?)/[^\s]+)',  # Path-like patterns
    ]
    
    COMPONENT_PATTERNS = [
        r'`([A-Z][a-zA-Z0-9]+Component)`',  # Backticked React/Blazor components
        r'([A-Z][a-zA-Z0-9]+(?:Button|Panel|Modal|Dialog|Form|Input|Select|Table|List|Card|View))',  # UI components
        r'([A-Z][a-zA-Z0-9]+Service)',  # Services
        r'([A-Z][a-zA-Z0-9]+Manager)',  # Managers
        r'([A-Z][a-zA-Z0-9]+Controller)',  # Controllers
    ]
    
    FEATURE_PATTERNS = [
        r'"([^"]+)"',  # Quoted features
        r'add (?:a |an )?([a-z][a-z\s]+(?:button|feature|export|panel|dashboard|authentication|login|system))',  # "add X" patterns
        r'implement (?:a |an )?([a-z][a-z\s]+)',  # "implement X" patterns
        r'create (?:a |an )?([a-z][a-z\s]+)',  # "create X" patterns
    ]
    
    # Common words to exclude from entity extraction
    STOPWORDS = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'be',
        'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
        'would', 'should', 'could', 'may', 'might', 'can', 'this', 'that',
        'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'test'
    }
    
    def __init__(self):
        """Initialize EntityExtractor"""
        pass
    
    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """
        Extract all entities from text
        
        Args:
            text: Message text to analyze
        
        Returns:
            Dictionary with entity types as keys and lists of entities as values
            Example: {
                'files': ['HostControlPanel.razor', 'app.css'],
                'components': ['FABButton', 'UserPanel'],
                'features': ['dark mode', 'export to PDF']
            }
        """
        entities = {
            'files': [],
            'components': [],
            'features': []
        }
        
        # Extract files
        for pattern in self.FILE_PATTERNS:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                # Handle tuple results from groups
                filename = match[0] if isinstance(match, tuple) else match
                if filename and filename not in entities['files']:
                    entities['files'].append(filename)
        
        # Extract components
        for pattern in self.COMPONENT_PATTERNS:
            matches = re.findall(pattern, text)
            for match in matches:
                if match and match not in entities['components']:
                    entities['components'].append(match)
        
        # Extract features
        for pattern in self.FEATURE_PATTERNS:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                # Clean up the match
                feature = match.strip().lower()
                
                # Skip if just stopwords
                words = feature.split()
                if all(w in self.STOPWORDS for w in words):
                    continue
                
                # Skip single letter or very short
                if len(feature) < 3:
                    continue
                
                if feature and feature not in entities['features']:
                    entities['features'].append(feature)
        
        return entities
    
    def extract_primary_entity(self, text: str) -> Optional[str]:
        """
        Extract the primary entity being discussed
        
        Heuristic: First file, component, or feature mentioned
        
        Args:
            text: Message text to analyze
        
        Returns:
            Primary entity string, or None if no entities found
        """
        entities = self.extract_entities(text)
        
        # Priority: files > components > features
        if entities['files']:
            return entities['files'][0]
        elif entities['components']:
            return entities['components'][0]
        elif entities['features']:
            return entities['features'][0]
        
        return None
    
    def resolve_reference(
        self,
        reference: str,
        context: Dict[str, Any]
    ) -> Optional[str]:
        """
        Resolve ambiguous reference ("it", "that", "the button") to actual entity
        
        Args:
            reference: Ambiguous reference from user message
            context: Context dictionary from ConversationManager
                     Contains recent_messages, primary_entity, related_files
        
        Returns:
            Resolved entity string, or None if cannot resolve
        """
        ref_lower = reference.lower().strip()
        
        # Direct pronoun mapping
        if ref_lower in ('it', 'this', 'that'):
            # Use primary entity from conversation
            return context.get('primary_entity')
        
        # Partial match against recent entities
        if ref_lower.startswith('the '):
            partial = ref_lower[4:]  # Remove "the "
            
            # Check recent messages for matching entities
            for msg in context.get('recent_messages', []):
                content = msg.get('content', '')
                entities = self.extract_entities(content)
                
                # Check all entity types
                for entity_list in entities.values():
                    for entity in entity_list:
                        if partial in entity.lower():
                            return entity
        
        # Check against related files
        related_files = context.get('related_files', [])
        for filepath in related_files:
            if reference.lower() in filepath.lower():
                return filepath
        
        # If no match, return reference as-is (might be new entity)
        return reference
    
    def extract_file_references(self, text: str) -> List[str]:
        """
        Extract only file references from text
        
        Args:
            text: Message text to analyze
        
        Returns:
            List of file paths mentioned
        """
        files = []
        
        for pattern in self.FILE_PATTERNS:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                filename = match[0] if isinstance(match, tuple) else match
                if filename and filename not in files:
                    files.append(filename)
        
        return files
    
    def deduplicate_entities(self, entities: List[str]) -> List[str]:
        """
        Remove duplicate and similar entities
        
        Args:
            entities: List of entity strings
        
        Returns:
            Deduplicated list
        """
        # Use set for exact deduplication
        unique = []
        seen = set()
        
        for entity in entities:
            entity_lower = entity.lower()
            if entity_lower not in seen:
                unique.append(entity)
                seen.add(entity_lower)
        
        return unique
    
    def categorize_files(self, filepaths: List[str]) -> Dict[str, List[str]]:
        """
        Categorize files by type
        
        Args:
            filepaths: List of file paths
        
        Returns:
            Dictionary with categories: {
                'source': [...],
                'tests': [...],
                'config': [...],
                'documentation': [...]
            }
        """
        categories = {
            'source': [],
            'tests': [],
            'config': [],
            'documentation': []
        }
        
        for filepath in filepaths:
            path_lower = filepath.lower()
            
            # Check for test files
            if 'test' in path_lower or 'spec' in path_lower:
                categories['tests'].append(filepath)
            
            # Check for config files
            elif any(ext in path_lower for ext in ['.json', '.yaml', '.yml', '.xml', '.config', '.toml']):
                categories['config'].append(filepath)
            
            # Check for documentation
            elif any(ext in path_lower for ext in ['.md', '.txt', '.rst', '.adoc']):
                categories['documentation'].append(filepath)
            
            # Otherwise, source file
            else:
                categories['source'].append(filepath)
        
        return categories
    
    def build_entity_summary(self, entities: Dict[str, List[str]]) -> str:
        """
        Build human-readable summary of extracted entities
        
        Args:
            entities: Dictionary of entities by type
        
        Returns:
            Summary string like "2 files, 3 components, 1 feature"
        """
        parts = []
        
        for entity_type, entity_list in entities.items():
            count = len(entity_list)
            if count > 0:
                type_singular = entity_type.rstrip('s')  # files -> file
                parts.append(f"{count} {type_singular if count == 1 else entity_type}")
        
        return ', '.join(parts) if parts else 'no entities'
    
    def extract_intents(self, text: str) -> List[str]:
        """
        Extract action intents from text
        
        Args:
            text: Message text to analyze
        
        Returns:
            List of detected intents (PLAN, EXECUTE, TEST, etc.)
        """
        text_lower = text.lower()
        intents = []
        
        # PLAN intent patterns
        if any(word in text_lower for word in ['i want', 'add a', 'create a', 'implement', 'build', 'design']):
            intents.append('PLAN')
        
        # EXECUTE intent patterns
        if any(word in text_lower for word in ['continue', 'next', 'keep going', 'proceed', 'execute']):
            intents.append('EXECUTE')
        
        # TEST intent patterns
        if any(word in text_lower for word in ['test', 'verify', 'validate', 'check']):
            intents.append('TEST')
        
        # CORRECT intent patterns
        if any(word in text_lower for word in ['wrong', 'not that', 'actually', 'correction', 'fix', 'oops']):
            intents.append('CORRECT')
        
        # RESUME intent patterns
        if any(word in text_lower for word in ['resume', 'where was i', 'status', 'progress']):
            intents.append('RESUME')
        
        # ASK intent patterns
        if '?' in text or any(word in text_lower for word in ['how do i', 'what is', 'explain', 'tell me']):
            intents.append('ASK')
        
        # Default to PLAN if no specific intent detected
        if not intents:
            intents.append('PLAN')
        
        return intents
