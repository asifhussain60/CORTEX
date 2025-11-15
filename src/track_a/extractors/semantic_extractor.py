"""
Semantic Extractor
==================

Purpose: Extract semantic information from parsed conversations including
entities, intents, patterns, and quality assessment.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file
"""

import re
from typing import Dict, List, Set, Optional
from datetime import datetime
import logging


logger = logging.getLogger(__name__)


class SemanticExtractor:
    """
    Extract semantic information from conversations for CORTEX learning.
    
    Extractions:
    1. Entities: Files, classes, functions, variables mentioned
    2. Intents: User intent patterns (PLAN, EXECUTE, TEST, VALIDATE, etc.)
    3. Patterns: Workflow patterns, problem-solution pairs
    4. Quality Score: Strategic value assessment (1-10 scale)
    
    Output format:
    {
        "entities": [
            {"type": "file", "value": "conversation_importer.py", "confidence": 0.9},
            {"type": "class", "value": "ConversationImporter", "confidence": 0.95}
        ],
        "intents": [
            {"intent": "EXECUTE", "confidence": 0.85, "message_index": 0}
        ],
        "patterns": [
            {
                "type": "workflow",
                "name": "conversation_import_workflow",
                "steps": ["validate", "parse", "extract", "store"],
                "confidence": 0.8
            }
        ],
        "quality_score": 8.5,
        "quality_factors": {
            "has_code_examples": true,
            "has_problem_solution": true,
            "multi_turn": true,
            "technical_depth": "high"
        }
    }
    """
    
    # Intent detection keywords
    INTENT_KEYWORDS = {
        "PLAN": ["plan", "design", "architect", "how should", "strategy"],
        "EXECUTE": ["add", "create", "implement", "build", "modify", "update"],
        "TEST": ["test", "verify", "validate", "check", "ensure"],
        "FIX": ["fix", "bug", "error", "broken", "issue", "problem"],
        "REFACTOR": ["refactor", "clean", "optimize", "improve", "restructure"],
        "ANALYZE": ["analyze", "investigate", "examine", "review", "assess"],
        "STATUS": ["status", "progress", "current state", "where are we", "what's the"],
        "EXPLAIN": ["explain", "how does", "what is", "why", "help me understand"]
    }
    
    def __init__(self):
        """Initialize SemanticExtractor."""
        logger.info("SemanticExtractor initialized")
    
    def extract(self, conversation: Dict) -> Dict:
        """
        Extract all semantic information from conversation.
        
        Args:
            conversation: Parsed conversation from CopilotParser
        
        Returns:
            Semantic data dictionary
        """
        messages = conversation.get("messages", [])
        
        if not messages:
            logger.warning("No messages to extract from")
            return self._empty_result()
        
        # Extract components
        entities = self._extract_entities(messages)
        intents_detailed = self._extract_intents(messages)
        patterns = self._extract_patterns(messages)
        quality_score, quality_factors = self._assess_quality(
            messages, entities, intents_detailed, patterns
        )
        
        # Create backward-compatible intents list (simple strings)
        intents_simple = list(set(intent["intent"] for intent in intents_detailed))
        
        result = {
            "entities": entities,
            "intents": intents_simple,  # Backward-compatible: ["EXECUTE", "PLAN"]
            "intents_detailed": intents_detailed,  # Detailed version with confidence
            "patterns": patterns,
            "quality": quality_score,  # Backward-compatible field name
            "quality_score": quality_score,  # Also keep new name for consistency
            "quality_factors": quality_factors,
            "extracted_at": datetime.now().isoformat()
        }
        
        logger.info(
            f"Extraction complete: {len(entities)} entities, "
            f"{len(intents_simple)} intents, quality={quality_score:.1f}"
        )
        
        return result
    
    def _extract_entities(self, messages: List[Dict]) -> List[Dict]:
        """
        Extract entities (files, classes, functions, variables).
        
        Entity types:
        - file: File paths and names (.py, .js, .md, etc.)
        - class: Class names (PascalCase)
        - function: Function names (snake_case or camelCase)
        - variable: Variable names
        - module: Module/package names
        """
        entities = []
        seen = set()  # Avoid duplicates
        
        for msg_idx, msg in enumerate(messages):
            content = msg["content"]
            
            # Extract files
            file_pattern = r'\b[\w\-/\\]+\.(py|js|ts|md|yaml|json|txt|cs|java|cpp|h)\b'
            for match in re.finditer(file_pattern, content):
                file_name = match.group(0)
                if file_name not in seen:
                    entities.append({
                        "type": "file",
                        "value": file_name,
                        "confidence": 0.9,
                        "message_index": msg_idx
                    })
                    seen.add(file_name)
            
            # Extract method names FIRST (PascalCase or camelCase with parens - C#, Java, etc.)
            # Must check BEFORE class extraction to avoid false positives
            # Handles both MethodName( and MethodName (with space)
            method_pattern = r'\b[A-Z][a-zA-Z0-9]*\s*\('
            for match in re.finditer(method_pattern, content):
                method_name = match.group(0).split('(')[0].strip()
                if method_name not in seen and method_name not in ["I", "API", "HTTP", "JSON", "URL"]:
                    entities.append({
                        "type": "method",
                        "value": method_name,
                        "confidence": 0.75,
                        "message_index": msg_idx
                    })
                    seen.add(method_name)
            
            # Extract function names (snake_case with parens or following patterns)
            func_pattern = r'\b[a-z_][a-z0-9_]*\s*\('
            for match in re.finditer(func_pattern, content):
                func_name = match.group(0).split('(')[0].strip()
                if func_name not in seen and not func_name.startswith("_"):
                    entities.append({
                        "type": "function",
                        "value": func_name,
                        "confidence": 0.75,
                        "message_index": msg_idx
                    })
                    seen.add(func_name)
            
            # Extract class names (PascalCase) - AFTER method extraction
            class_pattern = r'\b[A-Z][a-zA-Z0-9]*(?:[A-Z][a-zA-Z0-9]*)+\b'
            for match in re.finditer(class_pattern, content):
                class_name = match.group(0)
                # Filter out common false positives
                if class_name not in ["I", "API", "HTTP", "JSON", "URL"] and class_name not in seen:
                    entities.append({
                        "type": "class",
                        "value": class_name,
                        "confidence": 0.85,
                        "message_index": msg_idx
                    })
                    seen.add(class_name)
        
        return entities
    
    def _extract_intents(self, messages: List[Dict]) -> List[Dict]:
        """
        Detect user intents from messages.
        
        Returns list of detected intents with confidence scores.
        """
        intents = []
        
        for msg_idx, msg in enumerate(messages):
            if msg["role"] != "user":
                continue
            
            content = msg["content"].lower()
            
            # Check each intent type
            for intent_type, keywords in self.INTENT_KEYWORDS.items():
                matches = sum(1 for kw in keywords if kw in content)
                
                if matches > 0:
                    confidence = min(0.95, 0.6 + (matches * 0.15))
                    
                    intents.append({
                        "intent": intent_type,
                        "confidence": confidence,
                        "message_index": msg_idx,
                        "keywords_matched": matches
                    })
        
        return intents
    
    def _extract_patterns(self, messages: List[Dict]) -> List[Dict]:
        """
        Extract workflow patterns and problem-solution pairs.
        
        Patterns:
        - Workflow: Multi-step processes described
        - Problem-Solution: Issue + fix pairs
        - Question-Answer: Knowledge exchange
        """
        patterns = []
        
        # Detect workflow patterns (numbered lists, sequential steps)
        for msg_idx, msg in enumerate(messages):
            content = msg["content"]
            
            # Look for numbered steps
            step_pattern = r'(?:^|\n)\s*\d+\.\s+(.+?)(?=\n\s*\d+\.|\n\n|$)'
            steps = re.findall(step_pattern, content, re.MULTILINE | re.DOTALL)
            
            if len(steps) >= 3:
                patterns.append({
                    "type": "workflow",
                    "name": "multi_step_process",
                    "steps": [s.strip()[:50] for s in steps],  # First 50 chars
                    "step_count": len(steps),
                    "confidence": 0.8,
                    "message_index": msg_idx
                })
        
        # Detect problem-solution pairs
        for i in range(len(messages) - 1):
            user_msg = messages[i]
            assistant_msg = messages[i + 1]
            
            if user_msg["role"] == "user" and assistant_msg["role"] == "assistant":
                # Check if user message contains problem keywords
                problem_keywords = ["error", "issue", "problem", "bug", "broken", "fail"]
                user_content_lower = user_msg["content"].lower()
                
                has_problem = any(kw in user_content_lower for kw in problem_keywords)
                
                if has_problem:
                    patterns.append({
                        "type": "problem_solution",
                        "problem_summary": user_msg["content"][:100],
                        "solution_summary": assistant_msg["content"][:100],
                        "confidence": 0.7,
                        "message_indices": [i, i + 1]
                    })
        
        return patterns
    
    def _assess_quality(
        self,
        messages: List[Dict],
        entities: List[Dict],
        intents: List[Dict],
        patterns: List[Dict]
    ) -> tuple[float, Dict]:
        """
        Assess strategic value of conversation for CORTEX learning.
        
        Quality factors (1-10 scale):
        - Code examples: +2
        - Problem-solution pairs: +2
        - Multi-turn conversation: +1
        - High entity count: +2
        - Clear intents: +1
        - Workflow patterns: +2
        
        Returns:
            Tuple of (quality_score, quality_factors_dict)
        """
        score = 5.0  # Base score
        factors = {}
        
        # Factor 1: Has code blocks
        has_code = any("```" in msg["content"] for msg in messages)
        if has_code:
            score += 2
            factors["has_code_examples"] = True
        
        # Factor 2: Problem-solution pairs
        problem_solution_count = sum(
            1 for p in patterns if p["type"] == "problem_solution"
        )
        if problem_solution_count > 0:
            score += 2
            factors["has_problem_solution"] = True
        
        # Factor 3: Multi-turn (>4 messages)
        is_multi_turn = len(messages) > 4
        if is_multi_turn:
            score += 1
            factors["is_multi_turn"] = True
        
        # Factor 4: High entity count (>10 unique entities)
        if len(entities) > 10:
            score += 2
            factors["high_entity_count"] = True
        elif len(entities) > 5:
            score += 1
            factors["moderate_entity_count"] = True
        
        # Factor 5: Clear intents
        if len(intents) > 0:
            avg_confidence = sum(i["confidence"] for i in intents) / len(intents)
            if avg_confidence > 0.8:
                score += 1
                factors["clear_intents"] = True
        
        # Factor 6: Workflow patterns
        workflow_count = sum(1 for p in patterns if p["type"] == "workflow")
        if workflow_count > 0:
            score += 2
            factors["has_workflows"] = True
        
        # Determine technical depth
        tech_keywords = ["architecture", "design", "algorithm", "optimization", "pattern"]
        tech_mentions = sum(
            1 for msg in messages
            for kw in tech_keywords
            if kw in msg["content"].lower()
        )
        
        if tech_mentions >= 3:
            factors["technical_depth"] = "high"
        elif tech_mentions >= 1:
            factors["technical_depth"] = "medium"
        else:
            factors["technical_depth"] = "low"
        
        # Cap at 10
        score = min(10.0, score)
        
        return score, factors
    
    def _empty_result(self) -> Dict:
        """Return empty result structure."""
        return {
            "entities": [],
            "intents": [],  # Backward-compatible: simple list
            "intents_detailed": [],  # Detailed version
            "patterns": [],
            "quality": 0.0,  # Backward-compatible field name
            "quality_score": 0.0,  # Also keep new name
            "quality_factors": {},
            "extracted_at": datetime.now().isoformat()
        }
