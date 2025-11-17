"""
CORTEX Tier 1: Entity Extractor
Extracts entities from conversation text

Task 1.3: EntityExtractor
Duration: 1.5 hours
"""

import re
from typing import List, Set, Dict
from pathlib import Path


class EntityExtractor:
    """
    Extracts meaningful entities from conversation text
    
    Entity types:
    - File paths (e.g., src/main.py, cortex-brain/knowledge-graph.yaml)
    - Intent keywords (PLAN, EXECUTE, TEST, etc.)
    - Technical terms (dashboard, FAB button, migration, etc.)
    - Feature names (invoice export, dark mode, etc.)
    """
    
    # Known intent keywords
    INTENTS = {
        'PLAN', 'EXECUTE', 'TEST', 'VALIDATE', 'ASK', 
        'GOVERN', 'CORRECT', 'RESUME', 'COMMIT'
    }
    
    # Common technical terms in CORTEX context
    TECHNICAL_TERMS = {
        'dashboard', 'brain', 'tier', 'migration', 'agent',
        'conversation', 'pattern', 'knowledge', 'context',
        'hemisphere', 'workflow', 'validation', 'crawler',
        'session', 'sqlite', 'fts5', 'yaml', 'jsonl',
        'router', 'planner', 'executor', 'tdd', 'test'
    }
    
    def __init__(self):
        """Initialize entity extractor"""
        self.file_pattern = re.compile(
            r'(?:^|[\s\'"(])'  # Start or whitespace/quote/paren
            r'([a-zA-Z0-9_\-./\\]+\.[a-zA-Z0-9]+)'  # filename.ext
            r'(?:$|[\s\'")\]])',  # End or whitespace/quote/paren
            re.MULTILINE
        )
        
        self.feature_pattern = re.compile(
            r'\b([a-z]+(?:\s+[a-z]+){1,3})\b',  # 2-4 word phrases
            re.IGNORECASE
        )
    
    def extract_all(self, text: str) -> Dict[str, List[str]]:
        """
        Extract all entity types from text
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with entity types and lists
        """
        return {
            'files': self.extract_files(text),
            'intents': self.extract_intents(text),
            'technical_terms': self.extract_technical_terms(text),
            'features': self.extract_features(text)
        }
    
    def extract_files(self, text: str) -> List[str]:
        """
        Extract file paths from text
        
        Examples:
        - src/main.py
        - cortex-brain/knowledge-graph.yaml
        - CORTEX/src/tier1/conversation_manager.py
        
        Args:
            text: Text to analyze
            
        Returns:
            List of unique file paths
        """
        files = set()
        
        # Find file patterns
        matches = self.file_pattern.findall(text)
        for match in matches:
            # Filter out false positives
            if self._is_valid_file_path(match):
                files.add(match)
        
        return sorted(files)
    
    def _is_valid_file_path(self, path: str) -> bool:
        """
        Validate if string looks like a file path
        
        Args:
            path: Potential file path
            
        Returns:
            True if valid file path
        """
        # Must have extension
        if '.' not in path:
            return False
        
        # Check valid extensions
        valid_exts = {
            'py', 'md', 'yaml', 'yml', 'json', 'jsonl', 'txt',
            'sql', 'db', 'html', 'css', 'js', 'ts', 'tsx',
            'cs', 'csproj', 'ps1', 'sh', 'bash', 'xml'
        }
        
        ext = path.split('.')[-1].lower()
        if ext not in valid_exts:
            return False
        
        # Must not be just extension
        if len(path.split('.')[0]) < 2:
            return False
        
        return True
    
    def extract_intents(self, text: str) -> List[str]:
        """
        Extract intent keywords from text
        
        Examples:
        - PLAN
        - EXECUTE
        - TEST
        
        Args:
            text: Text to analyze
            
        Returns:
            List of intent keywords found
        """
        intents = set()
        
        # Look for known intents
        words = re.findall(r'\b[A-Z]+\b', text)
        for word in words:
            if word in self.INTENTS:
                intents.add(word)
        
        # Also check for lowercase versions in common patterns
        text_lower = text.lower()
        for intent in self.INTENTS:
            intent_lower = intent.lower()
            if intent_lower in text_lower:
                intents.add(intent)
        
        return sorted(intents)
    
    def extract_technical_terms(self, text: str) -> List[Dict[str, any]]:
        """
        Extract technical terms from text
        
        Examples:
        - dashboard
        - migration
        - pattern
        
        Args:
            text: Text to analyze
            
        Returns:
            List of dictionaries with term and frequency
        """
        terms = {}
        
        text_lower = text.lower()
        
        # Check for known technical terms
        for term in self.TECHNICAL_TERMS:
            if term in text_lower:
                # Count occurrences
                count = text_lower.count(term)
                terms[term] = terms.get(term, 0) + count
        
        # Also extract compound technical terms
        # e.g., "conversation-history", "knowledge-graph"
        compound_pattern = re.compile(r'\b([a-z]+-[a-z]+)\b', re.IGNORECASE)
        compounds = compound_pattern.findall(text)
        
        for compound in compounds:
            if len(compound) > 4:  # Filter short compounds
                term = compound.lower()
                terms[term] = terms.get(term, 0) + 1
        
        # Return as list of dicts
        return [{'term': term, 'count': count} for term, count in sorted(terms.items())]
    
    def extract_features(self, text: str) -> List[str]:
        """
        Extract feature names from text
        
        Examples:
        - "invoice export"
        - "dark mode"
        - "FAB button"
        
        Args:
            text: Text to analyze
            
        Returns:
            List of feature names
        """
        features = set()
        
        # Common feature patterns
        feature_keywords = {
            'add', 'create', 'implement', 'build', 'design',
            'fix', 'update', 'improve', 'enhance', 'refactor'
        }
        
        sentences = text.split('.')
        for sentence in sentences:
            sentence_lower = sentence.lower()
            
            # Look for "add X" or "create Y" patterns
            for keyword in feature_keywords:
                pattern = rf'\b{keyword}\s+(?:a\s+|an\s+|the\s+)?([a-z\s]+?)(?:\s+(?:to|for|in|with)|$)'
                matches = re.findall(pattern, sentence_lower, re.IGNORECASE)
                
                for match in matches:
                    match = match.strip()
                    # Keep 2-5 word feature names
                    words = match.split()
                    if 2 <= len(words) <= 5:
                        features.add(match)
        
        return sorted(features)
    
    def extract_entities_list(self, text: str) -> List[str]:
        """
        Extract all entities as a flat list (for backward compatibility)
        
        Args:
            text: Text to analyze
            
        Returns:
            Deduplicated list of all entities
        """
        all_entities = self.extract_all(text)
        
        # Flatten all entity types
        entities = set()
        for entity_list in all_entities.values():
            entities.update(entity_list)
        
        return sorted(entities)
    
    def extract_from_messages(self, messages: List[Dict]) -> List[str]:
        """
        Extract entities from a list of messages
        
        Args:
            messages: List of message dictionaries with 'content' or 'text' field
            
        Returns:
            Deduplicated list of all entities
        """
        all_text = []
        
        for msg in messages:
            # Support both 'content' and 'text' fields
            text = msg.get('content') or msg.get('text', '')
            if text:
                all_text.append(text)
        
        combined_text = ' '.join(all_text)
        return self.extract_entities_list(combined_text)
    
    def get_entity_frequency(self, text: str) -> Dict[str, int]:
        """
        Get entity frequency counts
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary mapping entities to counts
        """
        entities = self.extract_entities_list(text)
        
        frequency = {}
        text_lower = text.lower()
        
        for entity in entities:
            # Count occurrences (case-insensitive)
            count = text_lower.count(entity.lower())
            if count > 0:
                frequency[entity] = count
        
        return frequency
