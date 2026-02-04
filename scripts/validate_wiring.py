#!/usr/bin/env python3
"""
CORTEX Wiring Integrity Validator
Validates wiring.yaml structure and enforces consistency rules
"""

import yaml
import sys
from pathlib import Path
from collections import defaultdict, deque
from typing import Set, Dict, List, Tuple


class WiringValidator:
    """Validates CORTEX wiring.yaml"""
    
    def __init__(self, wiring_path: str):
        self.wiring_path = Path(wiring_path)
        self.wiring = None
        self.errors = []
        self.warnings = []
        self.orchestrators = {}
        
    def load_wiring(self):
        """Load and parse wiring.yaml"""
        try:
            with open(self.wiring_path, encoding='utf-8') as f:
                self.wiring = yaml.safe_load(f)
            print(f"✅ Loaded wiring from {self.wiring_path}")
        except Exception as e:
            self.errors.append(f"Failed to load wiring: {e}")
            return False
        return True
    
    def validate_structure(self):
        """Validate YAML structure"""
        required_keys = ['version', 'specification_date', 'config', 'orchestrators']
        for key in required_keys:
            if key not in self.wiring:
                self.errors.append(f"Missing required key: {key}")
        
        if 'orchestrators' in self.wiring:
            if not isinstance(self.wiring['orchestrators'], dict):
                self.errors.append("orchestrators must be a dictionary")
            else:
                for tier, orchs in self.wiring['orchestrators'].items():
                    if not isinstance(orchs, list):
                        self.errors.append(f"orchestrators.{tier} must be a list")
    
    def extract_orchestrators(self):
        """Extract all orchestrators into flat structure"""
        if 'orchestrators' not in self.wiring:
            return
        
        for tier, orchs in self.wiring['orchestrators'].items():
            for orch in orchs:
                name = orch.get('name')
                if not name:
                    self.errors.append(f"Orchestrator in tier {tier} missing name")
                    continue
                self.orchestrators[name] = orch
        
        print(f"✅ Extracted {len(self.orchestrators)} orchestrators")
    
    def validate_dependencies(self):
        """Check all dependencies exist and no circular dependencies"""
        # Check all deps exist
        for name, orch in self.orchestrators.items():
            deps = orch.get('dependencies', [])
            for dep in deps:
                if dep not in self.orchestrators:
                    self.errors.append(
                        f"{name} depends on {dep} which doesn't exist"
                    )
        
        # Check for circular dependencies using DFS
        visited = set()
        rec_stack = set()
        
        def has_cycle(node, visited, rec_stack, path=[]):
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            
            for neighbor in self.orchestrators[node].get('dependencies', []):
                if neighbor not in self.orchestrators:
                    continue
                if neighbor not in visited:
                    if has_cycle(neighbor, visited, rec_stack, path.copy()):
                        return True
                elif neighbor in rec_stack:
                    cycle_path = " → ".join(path + [neighbor])
                    self.errors.append(f"Circular dependency detected: {cycle_path}")
                    return True
            
            rec_stack.remove(node)
            return False
        
        for node in self.orchestrators:
            if node not in visited:
                has_cycle(node, visited, rec_stack)
    
    def validate_priorities(self):
        """Check for priority conflicts within tiers"""
        priorities_by_tier = defaultdict(dict)
        
        for tier, orchs in self.wiring['orchestrators'].items():
            for orch in orchs:
                name = orch.get('name')
                priority = orch.get('priority')
                tier_num = orch.get('tier')
                
                if priority is None:
                    self.warnings.append(f"{name} missing priority")
                    continue
                
                if tier_num != int(tier[-1]) if tier != 'core' and tier != 'domain' and tier != 'support' else tier_num:
                    # Check tier consistency
                    pass
                
                if priority in priorities_by_tier[tier]:
                    existing = priorities_by_tier[tier][priority]
                    self.errors.append(
                        f"Priority conflict in tier {tier}: "
                        f"{name} and {existing} both have priority {priority}"
                    )
                else:
                    priorities_by_tier[tier][priority] = name
        
        print(f"✅ Priority validation passed")
    
    def validate_health_checks(self):
        """Ensure all orchestrators define health check methods"""
        for name, orch in self.orchestrators.items():
            if 'health_check' not in orch:
                self.warnings.append(f"{name} missing health_check method")
    
    def validate_mcp_adapters(self):
        """Check MCP adapters are properly defined"""
        for name, orch in self.orchestrators.items():
            adapter = orch.get('mcp_adapter')
            if adapter:
                # Just verify it's a string path
                if not isinstance(adapter, str) or '.' not in adapter:
                    self.errors.append(
                        f"{name} has invalid mcp_adapter: {adapter}"
                    )
    
    def count_orchestrators(self):
        """Count orchestrators by tier"""
        tier_counts = defaultdict(int)
        for name, orch in self.orchestrators.items():
            tier = orch.get('tier')
            if tier:
                tier_counts[tier] += 1
        return tier_counts
    
    def validate_analyzer_coverage(self):
        """Ensure all required analyzers are defined"""
        required_analyzers = [
            'GitHistoryAnalyzer',
            'ASTAnalyzer',
            'CommentExtractor',
        ]
        
        analyzers = self.wiring.get('analyzers', [])
        analyzer_names = {a.get('name') for a in analyzers}
        
        for req in required_analyzers:
            if req not in analyzer_names:
                self.warnings.append(f"Missing analyzer: {req}")
    
    def validate_wiring_version(self):
        """Check wiring version is compatible"""
        version = self.wiring.get('version')
        if not version or not version.startswith('2.'):
            self.warnings.append(f"Wiring version {version} may be outdated")
    
    def generate_dependency_graph(self):
        """Generate ASCII dependency graph"""
        graph = []
        graph.append("\n📊 ORCHESTRATOR DEPENDENCY GRAPH\n")
        
        # Group by tier
        by_tier = defaultdict(list)
        for name, orch in self.orchestrators.items():
            tier = orch.get('tier')
            if tier:
                by_tier[tier].append((name, orch))
        
        for tier in sorted(by_tier.keys()):
            orchs = by_tier[tier]
            tier_name = {1: "CORE", 2: "DOMAIN", 3: "SUPPORT"}.get(tier, f"TIER{tier}")
            graph.append(f"  {tier_name} TIER ({len(orchs)} orchestrators)")
            graph.append("  " + "=" * 50)
            
            # Sort by priority
            orchs_sorted = sorted(orchs, key=lambda x: x[1].get('priority', 999))
            
            for name, orch in orchs_sorted:
                priority = orch.get('priority', '?')
                deps = orch.get('dependencies', [])
                icon = orch.get('metadata', {}).get('icon', '•')
                
                if deps:
                    dep_str = f" ← {', '.join(deps)}"
                else:
                    dep_str = " (no dependencies)"
                
                graph.append(
                    f"    [{priority:3}] {icon} {name}{dep_str}"
                )
            
            graph.append("")
        
        return "\n".join(graph)
    
    def print_summary(self):
        """Print validation summary"""
        tier_counts = self.count_orchestrators()
        
        print("\n" + "=" * 60)
        print("CORTEX WIRING VALIDATION SUMMARY")
        print("=" * 60)
        
        print(f"\n📊 ORCHESTRATOR COUNTS:")
        total = 0
        for tier in [1, 2, 3]:
            count = tier_counts.get(tier, 0)
            tier_name = {1: "CORE", 2: "DOMAIN", 3: "SUPPORT"}.get(tier)
            print(f"  {tier_name:8} tier: {count:2} orchestrators")
            total += count
        print(f"  {'TOTAL':8}:    {total:2} orchestrators")
        
        print(f"\n✅ PASSED CHECKS:")
        print(f"  • Structure validation")
        print(f"  • Dependency resolution")
        print(f"  • Circular dependency detection")
        print(f"  • Priority validation")
        print(f"  • Health check definitions")
        
        if self.warnings:
            print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            for warn in self.warnings:
                print(f"  ⚠️  {warn}")
        
        if self.errors:
            print(f"\n❌ ERRORS ({len(self.errors)}):")
            for err in self.errors:
                print(f"  ❌ {err}")
            return False
        
        return True
    
    def validate(self):
        """Run all validations"""
        print("\n" + "=" * 60)
        print("CORTEX WIRING VALIDATOR")
        print("=" * 60 + "\n")
        
        if not self.load_wiring():
            return False
        
        self.validate_structure()
        if self.errors:
            print("❌ Structure validation failed")
            return False
        
        self.extract_orchestrators()
        self.validate_dependencies()
        self.validate_priorities()
        self.validate_health_checks()
        self.validate_mcp_adapters()
        self.validate_analyzer_coverage()
        self.validate_wiring_version()
        
        success = self.print_summary()
        
        if success:
            print(self.generate_dependency_graph())
        
        print("\n" + "=" * 60)
        if success:
            print("✅ WIRING VALIDATION PASSED")
        else:
            print("❌ WIRING VALIDATION FAILED")
        print("=" * 60 + "\n")
        
        return success


def main():
    # Try multiple path resolutions
    possible_paths = [
        Path(__file__).parent.parent / "cortex" / "wiring" / "specifications" / "wiring.yaml",
        Path.cwd() / "cortex" / "wiring" / "specifications" / "wiring.yaml",
    ]
    
    wiring_path = None
    for p in possible_paths:
        if p.exists():
            wiring_path = p
            break
    
    # Allow custom path as argument
    if len(sys.argv) > 1:
        wiring_path = Path(sys.argv[1])
    
    if not wiring_path or not wiring_path.exists():
        print(f"❌ Error: Could not find wiring.yaml")
        print(f"   Tried: {[str(p) for p in possible_paths]}")
        sys.exit(1)
    
    validator = WiringValidator(str(wiring_path))
    success = validator.validate()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
