"""
CORTEX Session Rules Loader
MCP Tool for dynamic rule injection from registry

Purpose: Load applicable CORE rules at runtime based on user intent
Authority: Registry-Driven Governance pattern
"""

import yaml
from pathlib import Path
from typing import Dict, Any, List


class SessionRulesLoader:
    """
    Loads governance rules dynamically from cortex-registry.
    
    Replaces static prompt-embedded rules with runtime registry lookups.
    """
    
    def __init__(self):
        self.workspace_root = Path.cwd()
        self.registry_root = self.workspace_root / "cortex-registry"
    
    def load_rules_for_intent(self, intent: str) -> Dict[str, Any]:
        """
        Load applicable CORE rules for given intent.
        
        Args:
            intent: User intent (IMPLEMENT, FIX, REFACTOR, etc.)
        
        Returns:
            Dict containing:
            - core_rules: List of applicable CORE rule objects
            - enforcement_patterns: Relevant enforcement patterns
            - mcp_routing: Tool routing for this intent
            - response_format: Response standards
        """
        result = {
            "intent": intent,
            "core_rules": [],
            "enforcement_patterns": [],
            "mcp_routing": {},
            "response_format": {},
            "loaded_from": "cortex-registry"
        }
        
        # Load CORE rules
        core_rules_path = self.registry_root / "governance" / "core-rules.yaml"
        if core_rules_path.exists():
            try:
                with open(core_rules_path, 'r', encoding='utf-8') as f:
                    all_rules = yaml.safe_load(f)
                
                # Filter rules applicable to this intent
                result["core_rules"] = self._filter_rules_by_intent(all_rules, intent)
            except Exception as e:
                result["error"] = f"Failed to load CORE rules: {str(e)}"
        
        # Load enforcement patterns
        enforcement_path = self.registry_root / "governance" / "enforcement-patterns.yaml"
        if enforcement_path.exists():
            try:
                with open(enforcement_path, 'r', encoding='utf-8') as f:
                    patterns = yaml.safe_load(f)
                
                result["enforcement_patterns"] = self._filter_patterns_by_intent(patterns, intent)
            except Exception as e:
                result["error"] = f"Failed to load enforcement patterns: {str(e)}"
        
        # Load MCP routing
        routing_path = self.registry_root / "governance" / "mcp-routing.yaml"
        if routing_path.exists():
            try:
                with open(routing_path, 'r', encoding='utf-8') as f:
                    routing = yaml.safe_load(f)
                
                result["mcp_routing"] = routing.get("routing", {}).get(intent, {})
                result["native_tool_restrictions"] = routing.get("native_tool_restrictions", {}).get(intent, {})
            except Exception as e:
                result["error"] = f"Failed to load MCP routing: {str(e)}"
        
        # Load response formats
        response_path = self.registry_root / "interaction" / "response-formats.yaml"
        if response_path.exists():
            try:
                with open(response_path, 'r', encoding='utf-8') as f:
                    formats = yaml.safe_load(f)
                
                result["response_format"] = {
                    "header": formats.get("response_header", {}),
                    "progress_bar": formats.get("progress_bar", {}),
                    "completion_summary": formats.get("completion_summary", {}),
                    "status_icons": formats.get("status_icons", {})
                }
            except Exception as e:
                result["error"] = f"Failed to load response formats: {str(e)}"
        
        return result
    
    def _filter_rules_by_intent(self, all_rules: Dict, intent: str) -> List[Dict]:
        """
        Filter CORE rules applicable to intent.
        
        Intent-to-Rule mapping:
        - IMPLEMENT: CORE-008 (TDD), CORE-052 (Holistic), MCP-FIRST
        - FIX: CORE-008, CORE-030 (Implementation Truth), MCP-FIRST
        - REFACTOR: CORE-035 (Single Canonical), CORE-006, MCP-FIRST
        - ANALYZE: CORE-030 (Implementation Truth)
        - AUDIT: CORE-027 (Audit Trail)
        """
        intent_rule_map = {
            "IMPLEMENT": [
                "CORE-008",  # TDD-First
                "CORE-052",  # Holistic Validation Gate
                "CORE-011",  # Type hints
                "CORE-012",  # Docstrings
                "CORE-013",  # No bare except
                "CORE-027",  # Audit trail
                "MCP-FIRST", # MCP-FIRST enforcement
                "MCP-GATE"   # MCP gateway required
            ],
            "FIX": [
                "CORE-008",  # TDD-First
                "CORE-030",  # Implementation Truth
                "CORE-013",  # No bare except
                "CORE-027",  # Audit trail
                "MCP-FIRST"
            ],
            "REFACTOR": [
                "CORE-035",  # Single Canonical
                "CORE-006",  # Clean Code
                "CORE-051",  # Intelligence-Architecture Coupling
                "CORE-027",  # Audit trail
                "MCP-FIRST"
            ],
            "ANALYZE": [
                "CORE-030",  # Implementation Truth
                "CORE-036"   # Industry standards
            ],
            "AUDIT": [
                "CORE-027",  # Audit trail
                "CORE-052",  # Holistic validation
                "CORE-054"   # MCP tool wiring
            ],
            "DESIGN": [
                "CORE-048",  # Challenge Gate
                "CORE-036"   # Industry standards
            ],
            "PLAN": [
                "CORE-042"   # Hierarchical terminology
            ]
        }
        
        applicable_rule_ids = intent_rule_map.get(intent, [])
        
        # Extract rule details from all_rules
        filtered = []
        rules_dict = all_rules.get("rules", {})
        
        for rule_id in applicable_rule_ids:
            if rule_id in rules_dict:
                rule = rules_dict[rule_id]
                filtered.append({
                    "id": rule_id,
                    "title": rule.get("title", ""),
                    "principle": rule.get("principle", ""),
                    "enforcement": rule.get("enforcement", ""),
                    "rationale": rule.get("rationale", "")
                })
        
        return filtered
    
    def _filter_patterns_by_intent(self, patterns: Dict, intent: str) -> List[Dict]:
        """Filter enforcement patterns applicable to intent."""
        filtered = []
        
        # Check each pattern's trigger_intents
        for pattern_key, pattern in patterns.items():
            if isinstance(pattern, dict):
                trigger_intents = pattern.get("trigger_intents", [])
                
                if intent in trigger_intents or not trigger_intents:
                    filtered.append({
                        "id": pattern.get("pattern_id", pattern_key),
                        "title": pattern.get("title", ""),
                        "enforcement_level": pattern.get("enforcement_level", ""),
                        "trigger": pattern.get("trigger", ""),
                        "description": pattern.get("error_message", "")
                    })
        
        return filtered
    
    def format_rules_for_injection(self, rules_data: Dict) -> str:
        """
        Format loaded rules for injection into agent context.
        
        Returns markdown-formatted string ready for prompt injection.
        """
        sections = []
        
        # CORE Rules section
        if rules_data.get("core_rules"):
            sections.append("### 📋 Applicable CORE Rules")
            sections.append("")
            for rule in rules_data["core_rules"]:
                sections.append(f"**{rule['id']}: {rule['title']}**")
                sections.append(f"- Principle: {rule['principle']}")
                sections.append(f"- Enforcement: {rule['enforcement']}")
                sections.append("")
        
        # Enforcement patterns section
        if rules_data.get("enforcement_patterns"):
            sections.append("### 🛡️ Active Enforcement Patterns")
            sections.append("")
            for pattern in rules_data["enforcement_patterns"]:
                sections.append(f"**{pattern['id']}: {pattern['title']}**")
                sections.append(f"- Level: {pattern['enforcement_level']}")
                sections.append("")
        
        # MCP Routing section
        if rules_data.get("mcp_routing"):
            routing = rules_data["mcp_routing"]
            sections.append("### 🔧 MCP Tool Routing")
            sections.append("")
            sections.append(f"**Primary Tool:** {routing.get('primary_tool', 'N/A')}")
            sections.append(f"**Fallback:** {routing.get('fallback_behavior', 'N/A')}")
            sections.append("")
        
        # Native tool restrictions
        if rules_data.get("native_tool_restrictions"):
            restrictions = rules_data["native_tool_restrictions"]
            sections.append("### ⛔ Tool Restrictions")
            sections.append("")
            if restrictions.get("blocked"):
                sections.append(f"**Blocked:** {', '.join(restrictions['blocked'])}")
            if restrictions.get("allowed"):
                sections.append(f"**Allowed:** {', '.join(restrictions['allowed'])}")
            sections.append("")
        
        return "\n".join(sections)


# MCP Tool Entry Point
def cortex_get_session_rules(intent: str = "IMPLEMENT") -> Dict[str, Any]:
    """
    MCP Tool: Load governance rules dynamically from registry.
    
    Args:
        intent: User intent (IMPLEMENT, FIX, REFACTOR, etc.)
    
    Returns:
        Dict with rules, patterns, routing, and formatted context
    """
    loader = SessionRulesLoader()
    rules_data = loader.load_rules_for_intent(intent)
    
    # Add formatted version for prompt injection
    rules_data["formatted_context"] = loader.format_rules_for_injection(rules_data)
    
    return rules_data
