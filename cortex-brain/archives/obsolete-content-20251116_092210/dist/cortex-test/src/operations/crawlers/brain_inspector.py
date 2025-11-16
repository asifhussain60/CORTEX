"""
Brain Inspector Crawler

Analyzes CORTEX brain state across all tiers (Tier 1, 2, 3).
"""

import sqlite3
import yaml
from pathlib import Path
from typing import Dict, Any
from datetime import datetime

from .base_crawler import BaseCrawler


class BrainInspectorCrawler(BaseCrawler):
    """
    Inspects CORTEX brain to analyze:
    - Tier 1: Conversation memory (working memory)
    - Tier 2: Knowledge graph (learned patterns)
    - Tier 3: Development context (project metrics)
    - Brain health and protection rules
    """
    
    def get_name(self) -> str:
        return "Brain Inspector"
    
    def crawl(self) -> Dict[str, Any]:
        """
        Analyze CORTEX brain state across all tiers.
        
        Returns:
            Dict containing brain analysis
        """
        self.log_info("Starting brain inspection")
        
        brain_data = {
            'tier1': self._inspect_tier1(),
            'tier2': self._inspect_tier2(),
            'tier3': self._inspect_tier3(),
            'protection_rules': self._count_protection_rules(),
            'brain_health': 0.0
        }
        
        # Calculate overall brain health score
        brain_data['brain_health'] = self._calculate_health(brain_data)
        
        self.log_info(f"Brain health: {brain_data['brain_health']:.1f}/10")
        
        return {
            "success": True,
            "data": brain_data
        }
    
    def _inspect_tier1(self) -> Dict[str, Any]:
        """
        Inspect Tier 1 (Working Memory) - conversation history.
        
        Returns:
            Dict with conversation statistics
        """
        tier1_data = {
            'conversations': 0,
            'oldest': None,
            'newest': None,
            'retention_rate': 0,
            'database_exists': False
        }
        
        # Check for conversation database
        db_path = Path(self.project_root) / 'cortex-brain' / 'conversation-history.db'
        
        if not db_path.exists():
            self.log_warning("Tier 1 database not found")
            return tier1_data
        
        tier1_data['database_exists'] = True
        
        try:
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            # Count conversations
            cursor.execute("SELECT COUNT(*) FROM conversations")
            tier1_data['conversations'] = cursor.fetchone()[0]
            
            # Get date range
            cursor.execute("""
                SELECT MIN(timestamp), MAX(timestamp) 
                FROM conversations
                WHERE timestamp IS NOT NULL
            """)
            oldest, newest = cursor.fetchone()
            
            if oldest:
                tier1_data['oldest'] = oldest
            if newest:
                tier1_data['newest'] = newest
            
            # Retention rate (assume target is 20 conversations)
            tier1_data['retention_rate'] = min(100, (tier1_data['conversations'] / 20) * 100)
            
            conn.close()
            
        except Exception as e:
            self.log_warning(f"Could not read Tier 1 database: {e}")
        
        return tier1_data
    
    def _inspect_tier2(self) -> Dict[str, Any]:
        """
        Inspect Tier 2 (Knowledge Graph) - learned patterns.
        
        Returns:
            Dict with knowledge graph statistics
        """
        tier2_data = {
            'knowledge_patterns': 0,
            'capabilities': 0,
            'architectural_patterns': 0,
            'lessons_learned': 0,
            'file_relationships': 0,
            'files_exist': []
        }
        
        cortex_brain = Path(self.project_root) / 'cortex-brain'
        
        # Check knowledge graph files
        knowledge_files = {
            'knowledge-graph.yaml': 'knowledge_patterns',
            'capabilities.yaml': 'capabilities',
            'architectural-patterns.yaml': 'architectural_patterns',
            'lessons-learned.yaml': 'lessons_learned',
            'file-relationships.yaml': 'file_relationships',
        }
        
        for filename, key in knowledge_files.items():
            file_path = cortex_brain / filename
            
            if file_path.exists():
                tier2_data['files_exist'].append(filename)
                
                try:
                    with open(file_path, 'r') as f:
                        data = yaml.safe_load(f)
                        
                    if isinstance(data, dict):
                        # Count top-level keys or items
                        tier2_data[key] = len(data)
                    elif isinstance(data, list):
                        tier2_data[key] = len(data)
                        
                except Exception as e:
                    self.log_warning(f"Could not read {filename}: {e}")
        
        return tier2_data
    
    def _inspect_tier3(self) -> Dict[str, Any]:
        """
        Inspect Tier 3 (Development Context) - project metrics.
        
        Returns:
            Dict with development context statistics
        """
        tier3_data = {
            'git_commits_tracked': 0,
            'test_coverage': 0.0,
            'file_relationships': 0,
            'development_context_exists': False
        }
        
        # Check development context file
        context_path = Path(self.project_root) / 'cortex-brain' / 'development-context.yaml'
        
        if not context_path.exists():
            self.log_warning("Tier 3 development context not found")
            return tier3_data
        
        tier3_data['development_context_exists'] = True
        
        try:
            with open(context_path, 'r') as f:
                context = yaml.safe_load(f)
            
            if isinstance(context, dict):
                # Extract metrics
                tier3_data['git_commits_tracked'] = context.get('git', {}).get('total_commits', 0)
                tier3_data['test_coverage'] = context.get('testing', {}).get('coverage', 0.0)
                tier3_data['file_relationships'] = context.get('files', {}).get('relationships', 0)
                
        except Exception as e:
            self.log_warning(f"Could not read development context: {e}")
        
        return tier3_data
    
    def _count_protection_rules(self) -> int:
        """
        Count active brain protection rules.
        
        Returns:
            Number of protection rules
        """
        rules_path = Path(self.project_root) / 'cortex-brain' / 'brain-protection-rules.yaml'
        
        if not rules_path.exists():
            self.log_warning("Brain protection rules not found")
            return 0
        
        try:
            with open(rules_path, 'r') as f:
                rules = yaml.safe_load(f)
            
            if isinstance(rules, dict) and 'rules' in rules:
                return len(rules['rules'])
            elif isinstance(rules, list):
                return len(rules)
            
        except Exception as e:
            self.log_warning(f"Could not read protection rules: {e}")
        
        return 0
    
    def _calculate_health(self, brain_data: Dict[str, Any]) -> float:
        """
        Calculate overall brain health score (0-10).
        
        Args:
            brain_data: Complete brain analysis data
            
        Returns:
            Health score from 0-10
        """
        score = 0.0
        max_score = 10.0
        
        # Tier 1 health (3 points)
        tier1 = brain_data['tier1']
        if tier1['database_exists']:
            score += 1.0
            if tier1['conversations'] > 0:
                score += 1.0
            if tier1['retention_rate'] >= 80:
                score += 1.0
        
        # Tier 2 health (4 points)
        tier2 = brain_data['tier2']
        if len(tier2['files_exist']) >= 3:
            score += 1.0
        if tier2['knowledge_patterns'] > 10:
            score += 1.0
        if tier2['capabilities'] > 10:
            score += 1.0
        if tier2['lessons_learned'] > 5:
            score += 1.0
        
        # Tier 3 health (2 points)
        tier3 = brain_data['tier3']
        if tier3['development_context_exists']:
            score += 1.0
            if tier3['git_commits_tracked'] > 100:
                score += 1.0
        
        # Protection rules (1 point)
        if brain_data['protection_rules'] >= 4:
            score += 1.0
        
        return score
