"""
CORTEX Directive Loader
Machine-readable directive loading system with token optimization
"""

import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


class DirectiveLoader:
    """Load and cache CORTEX directives with O(1) lookup"""

    def __init__(self, registry_path: str = "cortex-registry/_cortex-master"):
        self.registry_path = Path(registry_path)
        self.index_path = self.registry_path / "meta" / "directive-index.yaml"
        self.schema_path = self.registry_path / "directives" / "schema.json"
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._cache_ttl = 300  # 5 minutes

    def load_index(self) -> Dict[str, Any]:
        """Load directive index for O(1) lookup"""
        with open(self.index_path) as f:
            return yaml.safe_load(f)

    def load_directive(
        self,
        name: str,
        context_hints: Optional[List[str]] = None,
        version: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Load directive with context-aware pruning

        Args:
            name: Directive name (e.g., 'architect', 'cortex')
            context_hints: Intent patterns to filter capabilities (e.g., ['AUDIT', 'DESIGN'])
            version: Specific version or 'latest' (default)

        Returns:
            Pruned directive dict with only relevant sections
        """
        # Check cache
        cache_key = self._cache_key(name, context_hints, version)
        if cache_key in self._cache:
            cached = self._cache[cache_key]
            if self._is_cache_valid(cached):
                return cached['data']

        # Load index
        index = self.load_index()

        if name not in index['directives']:
            raise ValueError(f"Directive '{name}' not found in index")

        directive_meta = index['directives'][name]

        # Version check
        if version and version != directive_meta['version']:
            raise ValueError(f"Version mismatch: requested {version}, found {directive_meta['version']}")

        # Load full directive
        directive_path = self.registry_path / directive_meta['path']
        with open(directive_path) as f:
            directive = yaml.safe_load(f)

        # Context-aware pruning
        if context_hints:
            directive = self._prune_directive(directive, context_hints)

        # Cache result
        self._cache[cache_key] = {
            'data': directive,
            'timestamp': datetime.now(),
            'ttl': self._cache_ttl
        }

        return directive

    def _prune_directive(self, directive: Dict[str, Any], context_hints: List[str]) -> Dict[str, Any]:
        """
        Prune directive to only include relevant capabilities based on context

        Token reduction: 60-80% for single-intent requests
        """
        # Filter capabilities by intent patterns
        relevant_caps = []
        for cap in directive.get('capabilities', []):
            # Keep if matches any context hint
            if any(hint in str(cap) for hint in context_hints):
                relevant_caps.append(cap)

        if relevant_caps:
            directive['capabilities'] = relevant_caps

        # Filter agents by mode (if mode-specific agents exist)
        if 'agents' in directive and context_hints:
            relevant_agents = {}
            for mode in context_hints:
                if mode in directive['agents']:
                    relevant_agents[mode] = directive['agents'][mode]
            if relevant_agents:
                directive['agents'] = relevant_agents

        return directive

    def validate_directive(self, directive_path: Path) -> Dict[str, Any]:
        """
        Validate directive against JSON Schema

        Returns:
            {'valid': bool, 'errors': List[str], 'warnings': List[str]}
        """
        import jsonschema

        # Load schema
        with open(self.schema_path) as f:
            schema = json.load(f)

        # Load directive
        with open(directive_path) as f:
            directive = yaml.safe_load(f)

        errors = []
        warnings = []

        try:
            jsonschema.validate(directive, schema)
        except jsonschema.ValidationError as e:
            errors.append(str(e))

        # Token budget check
        token_budget = directive['context']['token_budget']
        actual_tokens = self._estimate_tokens(directive)
        if actual_tokens > token_budget * 1.2:  # 20% tolerance
            warnings.append(
                f"Token budget exceeded: {actual_tokens} > {token_budget} (declared)"
            )

        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings
        }

    def compile_directive(
        self,
        name: str,
        format: str = 'yaml'
    ) -> str:
        """
        Compile directive with inheritance resolution

        Args:
            name: Directive name
            format: Output format ('yaml', 'json', 'markdown')

        Returns:
            Compiled directive as string
        """
        directive = self.load_directive(name)

        # Resolve inheritance
        if 'composition' in directive and 'inherits_from' in directive['composition']:
            directive = self._resolve_inheritance(directive)

        # Format output
        if format == 'yaml':
            return yaml.dump(directive, default_flow_style=False)
        elif format == 'json':
            return json.dumps(directive, indent=2)
        elif format == 'markdown':
            return self._to_markdown(directive)
        else:
            raise ValueError(f"Unsupported format: {format}")

    def _resolve_inheritance(self, directive: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve 'inherits_from' directive composition"""
        inherits = directive['composition']['inherits_from']

        for parent_id in inherits:
            # Parse parent directive ID
            parent_name = parent_id.split('/')[2]  # cortex://directives/name/version
            parent = self.load_directive(parent_name)

            # Merge capabilities (child overrides parent)
            parent_caps = {cap['id']: cap for cap in parent.get('capabilities', [])}
            child_caps = {cap['id']: cap for cap in directive.get('capabilities', [])}
            merged_caps = {**parent_caps, **child_caps}
            directive['capabilities'] = list(merged_caps.values())

        return directive

    def _to_markdown(self, directive: Dict[str, Any]) -> str:
        """Generate human-readable markdown documentation"""
        md = f"# {directive['metadata']['id']}\n\n"
        md += f"**Version:** {directive['metadata']['version']}  \n"
        md += f"**Updated:** {directive['metadata']['last_updated']}  \n\n"

        md += "## Capabilities\n\n"
        for cap in directive.get('capabilities', []):
            md += f"### {cap['id'].replace('_', ' ').title()}\n\n"
            md += f"{cap['description']}\n\n"

            if cap.get('constraints'):
                md += "**Constraints:**\n"
                for constraint in cap['constraints']:
                    md += f"- {constraint}\n"
                md += "\n"

        md += "## Constraints\n\n"
        for rule in directive['constraints']['tier0_rules']:
            md += f"- {rule}\n"

        return md

    def _cache_key(self, name: str, context: Optional[List[str]], version: Optional[str]) -> str:
        """Generate cache key from parameters"""
        key_parts = [name, str(context), str(version)]
        return hashlib.md5('|'.join(key_parts).encode()).hexdigest()

    def _is_cache_valid(self, cached: Dict[str, Any]) -> bool:
        """Check if cached entry is still valid"""
        age = (datetime.now() - cached['timestamp']).seconds
        return age < cached['ttl']

    def _estimate_tokens(self, directive: Dict[str, Any]) -> int:
        """Rough token estimation (4 chars = 1 token)"""
        text = yaml.dump(directive)
        return len(text) // 4


# MCP Tool wrapper
def load_directive_tool(
    name: str,
    context_hints: Optional[str] = None,
    version: Optional[str] = None
) -> str:
    """
    MCP tool: Load CORTEX directive with context-aware pruning

    Args:
        name: Directive name (architect, cortex, etc.)
        context_hints: Comma-separated intent patterns (AUDIT,DESIGN)
        version: Specific version or omit for latest

    Returns:
        YAML-formatted directive
    """
    loader = DirectiveLoader()

    # Parse context hints
    hints = None
    if context_hints:
        hints = [h.strip() for h in context_hints.split(',')]

    # Load directive
    directive = loader.load_directive(name, hints, version)

    # Return as YAML
    return yaml.dump(directive, default_flow_style=False)
