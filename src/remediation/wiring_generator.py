"""
Wiring Generator - Auto-generate integration code for unwired features

Generates:
- response-templates.yaml entries
- CORTEX.prompt.md command documentation
- Example trigger mappings

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import re
from pathlib import Path
from typing import Dict, List, Optional


class WiringGenerator:
    """Generates integration code for unwired orchestrators/agents"""
    
    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
        self.templates_file = self.project_root / "cortex-brain" / "response-templates.yaml"
        self.prompt_file = self.project_root / ".github" / "prompts" / "CORTEX.prompt.md"
    
    def generate_wiring_suggestion(self, feature_name: str, feature_path: str, 
                                   docstring: Optional[str] = None) -> Dict[str, str]:
        """
        Generate wiring suggestions for an unwired feature
        
        Args:
            feature_name: Name of orchestrator/agent (e.g., "PaymentOrchestrator")
            feature_path: Path to feature file (e.g., "src/operations/modules/payment_orchestrator.py")
            docstring: Feature's docstring for context
        
        Returns:
            Dictionary with keys: yaml_template, prompt_section, triggers
        """
        # Extract feature purpose from docstring
        purpose = self._extract_purpose(docstring) if docstring else f"{feature_name} operations"
        
        # Generate template name (snake_case)
        template_name = self._to_snake_case(feature_name)
        
        # Generate suggested triggers
        triggers = self._generate_triggers(feature_name)
        
        # Generate YAML template entry
        yaml_template = self._generate_yaml_template(template_name, feature_name, purpose, triggers)
        
        # Generate CORTEX.prompt.md section
        prompt_section = self._generate_prompt_section(feature_name, purpose, triggers)
        
        return {
            "yaml_template": yaml_template,
            "prompt_section": prompt_section,
            "triggers": triggers,
            "template_name": template_name,
            "feature_name": feature_name,
            "purpose": purpose
        }
    
    def _extract_purpose(self, docstring: str) -> str:
        """Extract first sentence from docstring as purpose"""
        if not docstring:
            return "Feature operations"
        
        # Get first line that's not empty
        lines = [line.strip() for line in docstring.split('\n') if line.strip()]
        if not lines:
            return "Feature operations"
        
        first_line = lines[0]
        # Remove quotes, triple quotes
        first_line = first_line.strip('"\'')
        
        # Get first sentence
        match = re.match(r'^([^.!?]+[.!?])', first_line)
        if match:
            return match.group(1).strip()
        
        return first_line[:100]  # Truncate if too long
    
    def _to_snake_case(self, name: str) -> str:
        """Convert PascalCase/CamelCase to snake_case"""
        # Remove "Orchestrator" or "Agent" suffix
        name = re.sub(r'(Orchestrator|Agent)$', '', name)
        
        # Insert underscore before uppercase letters
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
    
    def _generate_triggers(self, feature_name: str) -> List[str]:
        """Generate suggested trigger phrases for a feature"""
        # Remove "Orchestrator" or "Agent" suffix
        base_name = re.sub(r'(Orchestrator|Agent)$', '', feature_name)
        
        # Split on uppercase letters
        words = re.findall(r'[A-Z][a-z]*', base_name)
        words_lower = [w.lower() for w in words]
        
        # Generate trigger variations
        triggers = []
        
        # Full name lowercase
        triggers.append(' '.join(words_lower))
        
        # With common verbs
        if len(words_lower) > 1:
            # "start X", "run X", "execute X"
            action_words = words_lower[1:]  # Skip first word if it's a verb
            action_phrase = ' '.join(action_words)
            
            if words_lower[0] not in ['start', 'run', 'execute', 'handle', 'process']:
                triggers.append(f"start {' '.join(words_lower)}")
            
            triggers.append(f"run {action_phrase}")
        
        return triggers[:3]  # Return top 3 suggestions
    
    def _generate_yaml_template(self, template_name: str, feature_name: str, 
                                purpose: str, triggers: List[str]) -> str:
        """Generate YAML template entry"""
        yaml = f"""# Suggested wiring for {feature_name}
# Add to cortex-brain/response-templates.yaml

{template_name}:
  name: "{feature_name}"
  triggers:
"""
        for trigger in triggers:
            yaml += f'    - "{trigger}"\n'
        
        yaml += f"""  response_type: "detailed"
  orchestrator: "{feature_name}"
  content: |
    # 🧠 CORTEX {feature_name}
    **Author:** Asif Hussain | **GitHub:** github.com/asifhussain60/CORTEX
    
    ---
    
    ## My Understanding Of Your Request
    {{{{understanding}}}}
    
    ## Challenge
    {{{{challenge}}}}
    
    ## Response
    {purpose}
    
    ## Your Request
    {{{{user_request}}}}
    
    ## Next Steps
    {{{{next_steps}}}}
"""
        return yaml
    
    def _generate_prompt_section(self, feature_name: str, purpose: str, 
                                 triggers: List[str]) -> str:
        """Generate CORTEX.prompt.md documentation section"""
        # Remove "Orchestrator" or "Agent" suffix for section title
        section_title = re.sub(r'(Orchestrator|Agent)$', '', feature_name)
        
        prompt = f"""# Suggested documentation for {feature_name}
# Add to .github/prompts/CORTEX.prompt.md

## 🔧 {section_title}

**Purpose:** {purpose}

**Commands:**
"""
        for trigger in triggers:
            prompt += f'- `{trigger}` - {purpose}\n'
        
        prompt += """
**Natural Language Examples:**
"""
        for trigger in triggers:
            prompt += f'- "{trigger}"\n'
        
        prompt += """
**How It Works:**
1. [Step 1 description]
2. [Step 2 description]
3. [Step 3 description]

**Output:**
- [Output description]

**See Also:** [Related documentation]
"""
        return prompt
    
    def generate_batch_suggestions(self, unwired_features: List[Dict[str, any]]) -> List[Dict[str, str]]:
        """
        Generate wiring suggestions for multiple unwired features
        
        Args:
            unwired_features: List of dicts with keys: name, path, docstring
        
        Returns:
            List of wiring suggestions (one per feature)
        """
        suggestions = []
        
        for feature in unwired_features:
            suggestion = self.generate_wiring_suggestion(
                feature_name=feature.get("name", "Unknown"),
                feature_path=feature.get("path", ""),
                docstring=feature.get("docstring")
            )
            suggestions.append(suggestion)
        
        return suggestions
