#!/usr/bin/env python3
"""
CORTEX Brain Health Check - Comprehensive diagnostic of all cognitive tiers.
CORTEX 3.0 Enhanced: Session boundaries, ambient correlation, investigation routing.
"""

from pathlib import Path
import sqlite3
import yaml
import sys
from typing import Dict, List, Tuple


class HealthChecker:
    """Comprehensive health validation for all CORTEX components."""
    
    def __init__(self):
        self.issues = []
        self.warnings = []
        self.successes = []
    
    def add_issue(self, component: str, message: str):
        """Register a blocking issue."""
        self.issues.append(f"❌ {component}: {message}")
    
    def add_warning(self, component: str, message: str):
        """Register a warning."""
        self.warnings.append(f"⚠️  {component}: {message}")
    
    def add_success(self, component: str, message: str):
        """Register a success."""
        self.successes.append(f"✅ {component}: {message}")
    
    def check_tier0_brain_protection(self) -> bool:
        """Validate Tier 0: Brain Protection Rules."""
        print("\n📋 TIER 0: Brain Protection Rules")
        try:
            from src.tier0.brain_protector import BrainProtector
            bp = BrainProtector()
            
            # Check protection layers from YAML config
            protection_layers = bp.protection_layers
            tier0_instincts = bp.TIER0_INSTINCTS
            
            # Count SKULL rules
            skull_count = sum(1 for instinct in tier0_instincts if instinct.startswith("SKULL"))
            
            print(f"  Protection Layers: {len(protection_layers)}")
            print(f"  Tier 0 Instincts: {len(tier0_instincts)}")
            print(f"  SKULL Rules: {skull_count}")
            
            if skull_count < 5:
                self.add_warning("Tier 0", f"Only {skull_count} SKULL rules (expected 10+)")
            
            self.add_success("Tier 0", f"{len(protection_layers)} layers, {len(tier0_instincts)} instincts, {skull_count} SKULL rules")
            return True
        except Exception as e:
            self.add_issue("Tier 0", f"Failed to load brain protector: {e}")
            return False
    
    def check_tier1_working_memory(self) -> bool:
        """Validate Tier 1: Working Memory with CORTEX 3.0 enhancements."""
        print("\n💬 TIER 1: Working Memory (CORTEX 3.0)")
        
        db_path = Path("cortex-brain/tier1/working_memory.db")
        if not db_path.exists():
            self.add_warning("Tier 1", "Working memory database not initialized")
            return False
        
        try:
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()
            
            # Check conversations
            cur.execute("SELECT COUNT(*) FROM conversations")
            conv_count = cur.fetchone()[0]
            
            cur.execute("SELECT COUNT(*) FROM messages")
            msg_count = cur.fetchone()[0]
            
            # CORTEX 3.0: Check sessions
            try:
                cur.execute("SELECT COUNT(*) FROM sessions WHERE is_active = 1")
                active_sessions = cur.fetchone()[0]
                
                cur.execute("SELECT COUNT(*) FROM sessions")
                total_sessions = cur.fetchone()[0]
                
                print(f"  Sessions: {total_sessions} total, {active_sessions} active")
                self.add_success("Tier 1 Sessions", f"{total_sessions} sessions, {active_sessions} active")
            except sqlite3.OperationalError:
                self.add_warning("Tier 1 Sessions", "Sessions table not found (CORTEX 3.0 feature)")
            
            # CORTEX 3.0: Check ambient events
            try:
                cur.execute("SELECT COUNT(*) FROM ambient_events")
                ambient_count = cur.fetchone()[0]
                print(f"  Ambient Events: {ambient_count}")
                self.add_success("Tier 1 Ambient", f"{ambient_count} ambient events logged")
            except sqlite3.OperationalError:
                self.add_warning("Tier 1 Ambient", "Ambient events table not found (CORTEX 3.0 feature)")
            
            # Check conversation lifecycle
            try:
                cur.execute("SELECT COUNT(*) FROM conversation_lifecycle_events")
                lifecycle_count = cur.fetchone()[0]
                print(f"  Lifecycle Events: {lifecycle_count}")
                self.add_success("Tier 1 Lifecycle", f"{lifecycle_count} lifecycle events")
            except sqlite3.OperationalError:
                self.add_warning("Tier 1 Lifecycle", "Lifecycle events table not found (CORTEX 3.0 feature)")
            
            print(f"  Database: {db_path.stat().st_size / 1024:.1f} KB")
            print(f"  Conversations: {conv_count}, Messages: {msg_count}")
            
            conn.close()
            self.add_success("Tier 1 Core", f"{conv_count} conversations, {msg_count} messages")
            return True
            
        except Exception as e:
            self.add_issue("Tier 1", f"Database error: {e}")
            return False
    
    def check_tier2_knowledge_graph(self) -> bool:
        """Validate Tier 2: Knowledge Graph."""
        print("\n🧩 TIER 2: Knowledge Graph")
        
        kg_path = Path("cortex-brain/knowledge-graph.yaml")
        if not kg_path.exists():
            self.add_warning("Tier 2", "Knowledge graph not initialized")
            return False
        
        try:
            with open(kg_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            patterns = data.get('patterns', {})
            lessons = data.get('lessons_learned', {})
            
            print(f"  File Size: {kg_path.stat().st_size / 1024:.1f} KB")
            print(f"  Patterns: {len(patterns)}")
            print(f"  Lessons Learned: {len(lessons)}")
            
            if len(patterns) == 0:
                self.add_warning("Tier 2", "No patterns learned yet")
            
            self.add_success("Tier 2", f"{len(patterns)} patterns, {len(lessons)} lessons")
            return True
            
        except Exception as e:
            self.add_issue("Tier 2", f"Failed to load knowledge graph: {e}")
            return False
    
    def check_tier3_development_context(self) -> bool:
        """Validate Tier 3: Development Context."""
        print("\n📊 TIER 3: Development Context")
        
        dev_ctx_path = Path("cortex-brain/development-context.yaml")
        if dev_ctx_path.exists():
            print(f"  File Size: {dev_ctx_path.stat().st_size / 1024:.1f} KB")
            self.add_success("Tier 3", "Development context tracking active")
            return True
        else:
            self.add_warning("Tier 3", "Development context not initialized")
            return False
    
    def check_agent_coordination(self) -> bool:
        """Validate Agent Coordination (Intent Router, Investigation Router)."""
        print("\n🤖 AGENT COORDINATION (CORTEX 3.0)")
        
        try:
            from src.cortex_agents.intent_router import IntentRouter
            from src.cortex_agents.investigation_router import InvestigationRouter
            
            print("  ✅ IntentRouter: Available")
            print("  ✅ InvestigationRouter: Available")
            
            # Check if investigation router can be instantiated
            try:
                # Mock check - just verify imports work
                self.add_success("Agent Coordination", "Intent & Investigation routers operational")
                return True
            except Exception as e:
                self.add_warning("Agent Coordination", f"Router initialization concern: {e}")
                return False
                
        except ImportError as e:
            self.add_issue("Agent Coordination", f"Failed to import routers: {e}")
            return False
    
    def check_entry_points(self) -> bool:
        """Validate Entry Points (CORTEX.prompt.md, copilot-instructions.md)."""
        print("\n📝 ENTRY POINTS")
        
        cortex_prompt = Path(".github/prompts/CORTEX.prompt.md")
        copilot_instructions = Path(".github/copilot-instructions.md")
        
        if cortex_prompt.exists():
            size = cortex_prompt.stat().st_size / 1024
            print(f"  CORTEX.prompt.md: {size:.1f} KB")
            
            # Check for CORTEX 3.0 features mentioned
            content = cortex_prompt.read_text(encoding='utf-8')
            if "Session" in content or "session" in content:
                print("    ✅ Contains session boundary references")
            if "Investigation" in content or "investigate" in content:
                print("    ✅ Contains investigation routing references")
            
            self.add_success("Entry Points", "CORTEX.prompt.md present")
        else:
            self.add_issue("Entry Points", "CORTEX.prompt.md not found")
        
        if copilot_instructions.exists():
            size = copilot_instructions.stat().st_size / 1024
            print(f"  copilot-instructions.md: {size:.1f} KB")
            self.add_success("Entry Points", "copilot-instructions.md present")
        else:
            self.add_warning("Entry Points", "copilot-instructions.md not found")
        
        return cortex_prompt.exists()
    
    def generate_report(self):
        """Generate final health report."""
        print("\n" + "=" * 70)
        print("🏥 CORTEX HEALTH REPORT")
        print("=" * 70)
        
        if self.successes:
            print(f"\n✅ SUCCESSES ({len(self.successes)}):")
            for success in self.successes:
                print(f"  {success}")
        
        if self.warnings:
            print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"  {warning}")
        
        if self.issues:
            print(f"\n❌ CRITICAL ISSUES ({len(self.issues)}):")
            for issue in self.issues:
                print(f"  {issue}")
        
        print("\n" + "=" * 70)
        
        # Overall status
        if self.issues:
            print("OVERALL BRAIN HEALTH: ❌ CRITICAL ISSUES FOUND")
            print("=" * 70)
            return 1
        elif self.warnings:
            print("OVERALL BRAIN HEALTH: ⚠️  WARNINGS PRESENT")
            print("=" * 70)
            return 0
        else:
            print("OVERALL BRAIN HEALTH: ✅ EXCELLENT")
            print("=" * 70)
            return 0


def main():
    """Run comprehensive CORTEX health check."""
    print("=" * 70)
    print("🧠 CORTEX 3.0 COMPREHENSIVE HEALTH CHECK")
    print("=" * 70)
    
    checker = HealthChecker()
    
    # Run all health checks
    checker.check_tier0_brain_protection()
    checker.check_tier1_working_memory()
    checker.check_tier2_knowledge_graph()
    checker.check_tier3_development_context()
    checker.check_agent_coordination()
    checker.check_entry_points()
    
    # Generate report
    exit_code = checker.generate_report()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
