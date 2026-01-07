"""
CORTEX Toolkit Capability Matrix

Maps tools to their capabilities for semantic overlap detection.
Used by RequestAnalyzer to prevent tool duplication.
"""
from typing import Dict, List, Set, Optional, Tuple
from dataclasses import dataclass, field
from pathlib import Path
import re
import logging

logger = logging.getLogger(__name__)


@dataclass
class ToolCapabilities:
    """Capabilities extracted from a tool."""
    name: str
    description: str
    category: str
    primary_capabilities: Set[str] = field(default_factory=set)
    secondary_capabilities: Set[str] = field(default_factory=set)
    keywords: Set[str] = field(default_factory=set)
    
    @property
    def all_capabilities(self) -> Set[str]:
        """Get all capabilities (primary + secondary)."""
        return self.primary_capabilities | self.secondary_capabilities


@dataclass
class ToolMatch:
    """A tool that matches a capability query."""
    name: str
    description: str
    category: str
    matched_capabilities: Set[str]
    similarity: float = 0.0
    
    def __repr__(self):
        return f"ToolMatch(name={self.name!r}, similarity={self.similarity:.2f})"


class CapabilityMatrix:
    """
    Maps tools to their capabilities for overlap detection.
    
    Uses a keyword taxonomy to categorize tools and find semantic overlaps.
    """
    
    # Primary capability categories with their keyword synonyms
    CAPABILITY_TAXONOMY = {
        # Maintenance & Cleanup
        'cleanup': {
            'keywords': ['clean', 'remove', 'delete', 'purge', 'clear', 'temp', 'cache', 'garbage'],
            'description': 'Cleaning up files, caches, or temporary data'
        },
        'maintenance': {
            'keywords': ['maintain', 'health', 'repair', 'fix', 'tune', 'optimize'],
            'description': 'System maintenance and health operations'
        },
        
        # Validation & Testing
        'validation': {
            'keywords': ['validate', 'check', 'verify', 'lint', 'syntax', 'error'],
            'description': 'Validating files, code, or configurations'
        },
        'testing': {
            'keywords': ['test', 'mock', 'assert', 'unit', 'integration', 'performance'],
            'description': 'Testing and test generation'
        },
        
        # Generation & Creation
        'generation': {
            'keywords': ['generate', 'create', 'build', 'scaffold', 'new', 'init'],
            'description': 'Generating code, files, or structures'
        },
        'documentation': {
            'keywords': ['doc', 'document', 'readme', 'markdown', 'html', 'reference'],
            'description': 'Documentation generation and management'
        },
        
        # Analysis & Profiling
        'analysis': {
            'keywords': ['analyze', 'inspect', 'profile', 'measure', 'metric', 'report'],
            'description': 'Analyzing code, performance, or data'
        },
        'visualization': {
            'keywords': ['visualize', 'chart', 'graph', 'diagram', 'uml', 'plot'],
            'description': 'Data visualization and diagram generation'
        },
        
        # Migration & Transformation
        'migration': {
            'keywords': ['migrate', 'upgrade', 'convert', 'transform', 'port', 'version'],
            'description': 'Data migration and transformation'
        },
        'schema': {
            'keywords': ['schema', 'model', 'entity', 'database', 'openapi', 'spec'],
            'description': 'Schema and specification management'
        },
        
        # Operations & Deployment
        'deployment': {
            'keywords': ['deploy', 'publish', 'release', 'package', 'install'],
            'description': 'Deployment and publishing operations'
        },
        'operations': {
            'keywords': ['review', 'sanitize', 'align', 'orchestrate', 'workflow'],
            'description': 'System operations and workflow management'
        },
        
        # Planning & Management
        'planning': {
            'keywords': ['plan', 'task', 'story', 'feature', 'sprint', 'ado', 'work item'],
            'description': 'Planning and project management'
        },
    }
    
    # Action verb mappings for intent extraction
    ACTION_VERBS = {
        'create': ['create', 'generate', 'make', 'build', 'scaffold', 'new', 'add'],
        'delete': ['delete', 'remove', 'clean', 'purge', 'clear', 'drop'],
        'update': ['update', 'modify', 'change', 'edit', 'fix', 'patch'],
        'validate': ['validate', 'check', 'verify', 'test', 'lint', 'ensure'],
        'analyze': ['analyze', 'inspect', 'profile', 'measure', 'review', 'audit'],
        'convert': ['convert', 'transform', 'migrate', 'export', 'import'],
    }
    
    def __init__(self, registry=None):
        """
        Initialize CapabilityMatrix.
        
        Args:
            registry: Optional ToolkitRegistry for loading tool data.
        """
        self.registry = registry
        self._tool_capabilities: Dict[str, ToolCapabilities] = {}
        self._keyword_index: Dict[str, Set[str]] = {}  # keyword -> tool names
        
        if registry:
            self._build_matrix()
    
    def _build_matrix(self):
        """Build capability matrix from registry tools."""
        if not self.registry:
            return
        
        tools = self.registry.list_tools()
        for tool in tools:
            capabilities = self._extract_capabilities(tool)
            self._tool_capabilities[tool['name']] = capabilities
            self._index_keywords(capabilities)
        
        logger.info(f"Built capability matrix with {len(self._tool_capabilities)} tools")
    
    def _extract_capabilities(self, tool: Dict) -> ToolCapabilities:
        """Extract capabilities from a tool definition."""
        name = tool.get('name', '')
        description = tool.get('description', '')
        category = self._get_tool_category(tool)
        
        # Combine name, description, and user-friendly info for analysis
        text = f"{name} {description}"
        if 'user_friendly_name' in tool:
            text += f" {tool['user_friendly_name']}"
        if 'functionality' in tool:
            text += f" {tool['functionality']}"
        
        text = text.lower()
        
        primary = set()
        secondary = set()
        keywords = set()
        
        # Match against taxonomy
        for capability, info in self.CAPABILITY_TAXONOMY.items():
            matched_keywords = []
            for keyword in info['keywords']:
                if keyword in text:
                    matched_keywords.append(keyword)
                    keywords.add(keyword)
            
            if len(matched_keywords) >= 2:
                primary.add(capability)
            elif matched_keywords:
                secondary.add(capability)
        
        # Use category as fallback capability
        category_map = {
            'brain_operations': 'maintenance',
            'operations': 'operations',
            'planning': 'planning',
            'analytics': 'analysis',
            'documentation': 'documentation',
            'testing': 'testing',
            'migration': 'migration',
            'maintenance': 'maintenance',
            'generators': 'generation',
            'utilities': 'operations',
        }
        
        if category in category_map:
            cap = category_map[category]
            if cap not in primary:
                secondary.add(cap)
        
        return ToolCapabilities(
            name=name,
            description=description,
            category=category,
            primary_capabilities=primary,
            secondary_capabilities=secondary,
            keywords=keywords
        )
    
    def _get_tool_category(self, tool: Dict) -> str:
        """Get the category a tool belongs to."""
        if not self.registry:
            return "unknown"
        
        for category in self.registry.list_categories():
            tools = self.registry.list_tools(category)
            if any(t['name'] == tool['name'] for t in tools):
                return category
        return "unknown"
    
    def _index_keywords(self, capabilities: ToolCapabilities):
        """Index tool by its keywords for fast lookup."""
        tool_name = capabilities.name
        
        for keyword in capabilities.keywords:
            if keyword not in self._keyword_index:
                self._keyword_index[keyword] = set()
            self._keyword_index[keyword].add(tool_name)
        
        for capability in capabilities.all_capabilities:
            if capability not in self._keyword_index:
                self._keyword_index[capability] = set()
            self._keyword_index[capability].add(tool_name)
    
    def find_overlaps(self, intent_keywords: List[str]) -> List[ToolMatch]:
        """
        Find tools with overlapping capabilities.
        
        Args:
            intent_keywords: Keywords describing the intended functionality.
            
        Returns:
            List of matching tools sorted by relevance.
        """
        intent_set = set(kw.lower() for kw in intent_keywords)
        
        # Find candidate tools
        candidate_tools: Dict[str, Set[str]] = {}  # tool -> matched keywords
        
        for keyword in intent_set:
            # Direct keyword match
            if keyword in self._keyword_index:
                for tool_name in self._keyword_index[keyword]:
                    if tool_name not in candidate_tools:
                        candidate_tools[tool_name] = set()
                    candidate_tools[tool_name].add(keyword)
            
            # Check capability taxonomy
            for capability, info in self.CAPABILITY_TAXONOMY.items():
                if keyword in info['keywords'] or keyword == capability:
                    if capability in self._keyword_index:
                        for tool_name in self._keyword_index[capability]:
                            if tool_name not in candidate_tools:
                                candidate_tools[tool_name] = set()
                            candidate_tools[tool_name].add(capability)
        
        # Build match results
        matches = []
        for tool_name, matched in candidate_tools.items():
            if tool_name not in self._tool_capabilities:
                continue
            
            tool_caps = self._tool_capabilities[tool_name]
            matches.append(ToolMatch(
                name=tool_name,
                description=tool_caps.description,
                category=tool_caps.category,
                matched_capabilities=matched
            ))
        
        # Sort by number of matches (descending)
        matches.sort(key=lambda m: len(m.matched_capabilities), reverse=True)
        
        return matches
    
    def extract_intent(self, description: str) -> List[str]:
        """
        Extract intent keywords from a natural language description.
        
        Args:
            description: Natural language description of desired functionality.
            
        Returns:
            List of extracted intent keywords.
        """
        description = description.lower()
        keywords = []
        
        # Extract action verbs
        for action, synonyms in self.ACTION_VERBS.items():
            if any(s in description for s in synonyms):
                keywords.append(action)
        
        # Extract capability keywords
        for capability, info in self.CAPABILITY_TAXONOMY.items():
            if any(kw in description for kw in info['keywords']):
                keywords.append(capability)
        
        # Extract specific nouns
        specific_patterns = [
            r'\b(cache|caches)\b',
            r'\b(temp|temporary)\b',
            r'\b(test|tests|testing)\b',
            r'\b(document|documentation|docs)\b',
            r'\b(schema|schemas)\b',
            r'\b(uml|diagram|diagrams)\b',
            r'\b(yaml|json|xml)\b',
            r'\b(html|css|javascript)\b',
            r'\b(api|endpoint|endpoints)\b',
            r'\b(database|db)\b',
        ]
        
        for pattern in specific_patterns:
            if re.search(pattern, description):
                match = re.search(pattern, description).group(1)
                keywords.append(match)
        
        return list(set(keywords))
    
    def get_tool_capabilities(self, tool_name: str) -> Optional[ToolCapabilities]:
        """Get capabilities for a specific tool."""
        return self._tool_capabilities.get(tool_name)
    
    def calculate_similarity(
        self, 
        caps1: Set[str], 
        caps2: Set[str]
    ) -> float:
        """
        Calculate Jaccard similarity between two capability sets.
        
        Args:
            caps1: First capability set.
            caps2: Second capability set.
            
        Returns:
            Similarity score between 0.0 and 1.0.
        """
        if not caps1 or not caps2:
            return 0.0
        
        intersection = len(caps1 & caps2)
        union = len(caps1 | caps2)
        
        return intersection / union if union > 0 else 0.0
    
    def get_all_capabilities(self) -> Set[str]:
        """Get all known capabilities."""
        return set(self.CAPABILITY_TAXONOMY.keys())
    
    def get_tools_by_capability(self, capability: str) -> List[str]:
        """Get all tools with a specific capability."""
        return list(self._keyword_index.get(capability, set()))
