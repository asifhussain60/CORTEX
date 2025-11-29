"""
CORTEX Scope Inference Engine

Purpose: Auto-extract feature boundaries from Planning DoR Q3 (functional scope) and Q6 (technical dependencies)
Target: <5 seconds execution time, >70% confidence for auto-proceed
Status: TDD GREEN Phase - Implementation to pass RED tests

Component of: SWAGGER Entry Point Module (Phase 3.2)
"""

import re
import logging
from dataclasses import dataclass, field
from typing import List, Dict, Set
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class ScopeEntities:
    """Detected entities from requirements"""
    tables: List[str] = field(default_factory=list)
    files: List[str] = field(default_factory=list)
    services: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    confidence_scores: Dict[str, float] = field(default_factory=dict)


@dataclass
class ScopeBoundary:
    """Scope boundary with safety limits"""
    table_count: int
    file_count: int
    service_count: int
    dependency_depth: int
    estimated_complexity: float  # 0-100 scale
    confidence: float  # 0-100 (0.0-1.0 internally)
    gaps: List[str] = field(default_factory=list)


class ScopeInferenceEngine:
    """
    Extract scope boundaries from Planning DoR answers
    
    Key Innovation: Zero new questions for 80% of cases - scope extracted from
    requirements already collected during DoR validation (Q3 + Q6)
    """
    
    # Safety limits (enterprise monolith protection)
    MAX_TABLES = 50
    MAX_FILES = 100
    MAX_DEPENDENCY_DEPTH = 2
    
    # Confidence thresholds
    HIGH_CONFIDENCE = 0.70
    MEDIUM_CONFIDENCE = 0.30
    
    def __init__(self):
        """Initialize entity detection patterns"""
        # Patterns for table detection
        self.table_patterns = [
            r'\b([A-Z][a-zA-Z0-9_]*?)\s+table',  # "Users table"
            r'table\s+([A-Z][a-zA-Z0-9_]+)',  # "table Users"
            r'\b([a-z][a-z0-9_]{3,})\s+table',  # "user_accounts table" (3+ chars)
            r'\bfields\s+to\s+([a-z][a-z0-9_]{3,})\b',  # "fields to user_accounts"
            r'table[:\s]+([A-Z][a-zA-Z0-9_]+)',  # "table: Users"
            r'\btables?:\s*([A-Za-z0-9_,\s-]+)',  # "tables: Users, user-profiles"
        ]
        
        # Patterns for file/class detection
        self.file_patterns = [
            r'\b([A-Z][a-zA-Z0-9\.]*\.[a-z]{2,4})\b',  # "UserService.cs" or "User.Service.cs"
            r'\b([A-Z][a-zA-Z0-9]*Service)\b',  # "UserService"
            r'\b([A-Z][a-zA-Z0-9]*Controller)\b',  # "AuthController"
            r'\b([A-Z][a-zA-Z0-9]*Manager)\b',  # "SessionManager"
            r'\b([A-Z][a-zA-Z0-9]*ViewModel)\b',  # "LoginViewModel"
            r'\b([a-z][a-z0-9_]*\.[a-z]{2,4})\b',  # "authentication.py"
        ]
        
        # Patterns for external services
        self.service_patterns = [
            r'(Azure\s+AD\s+B2C)',  # "Azure AD B2C" - specific first
            r'(Azure\s+AD)',  # "Azure AD" - general
            r'\b(SendGrid|Twilio|Redis|AWS|GCP)\b',  # Common services
            r'\b([A-Z][a-zA-Z]*)\s+API\b',  # "SendGrid API" - but capture name only
        ]
        
        # Patterns for technical dependencies
        self.dependency_patterns = [
            r'\b(OAuth\s*[0-9.]*|JWT|SMTP|bcrypt|Redis)\b',
            r'requires?\s+([A-Z][A-Za-z\s]*)',  # "requires OAuth"
            r'depends?\s+on\s+([A-Z][A-Za-z\s]*)',  # "depends on payment"
        ]
    
    def parse_dor_answers(self, dor_responses: Dict[str, str]) -> str:
        """
        Extract and combine text from DoR Q3 and Q6
        
        Args:
            dor_responses: Dict with 'Q3' and/or 'Q6' keys
            
        Returns:
            Combined requirements text for entity extraction
        """
        combined = []
        
        if 'Q3' in dor_responses:
            combined.append(dor_responses['Q3'])
        
        if 'Q6' in dor_responses:
            combined.append(dor_responses['Q6'])
        
        return '\n'.join(combined)
    
    def _contains_vague_keywords(self, text: str) -> bool:
        """Check if text contains vague keywords that indicate uncertainty"""
        vague_keywords = ['some', 'few', 'maybe', 'possibly', 'might', 'could', 
                         'several', 'various', 'certain', 'a few']
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in vague_keywords)
    
    def extract_entities(self, requirements_text: str) -> ScopeEntities:
        """
        Extract tables, files, services, dependencies from requirements
        
        Args:
            requirements_text: Requirements from DoR Q3 + Q6
            
        Returns:
            ScopeEntities with detected entities and confidence scores
        """
        entities = ScopeEntities()
        
        # Extract tables
        tables_set: Set[str] = set()
        tables_lower_map: Dict[str, str] = {}  # lowercase -> original for dedup
        
        for pattern in self.table_patterns:
            matches = re.finditer(pattern, requirements_text, re.IGNORECASE)
            for match in matches:
                if match.lastindex and match.lastindex >= 1:
                    table_name = match.group(1).strip()
                    # Handle comma-separated lists
                    if ',' in table_name:
                        for name in table_name.split(','):
                            clean_name = name.strip()
                            if clean_name:
                                # Deduplicate case-insensitively
                                lower_key = clean_name.lower()
                                if lower_key not in tables_lower_map:
                                    normalized = self._normalize_entity_name(clean_name)
                                    tables_lower_map[lower_key] = normalized
                                    tables_set.add(normalized)
                    else:
                        if table_name:
                            lower_key = table_name.lower()
                            if lower_key not in tables_lower_map:
                                normalized = self._normalize_entity_name(table_name)
                                tables_lower_map[lower_key] = normalized
                                tables_set.add(normalized)
        
        entities.tables = sorted(list(tables_set))
        
        # Extract files
        files_set: Set[str] = set()
        files_lower_map: Dict[str, str] = {}  # Deduplicate UserService vs UserService.cs
        
        for pattern in self.file_patterns:
            matches = re.finditer(pattern, requirements_text)
            for match in matches:
                if match.lastindex and match.lastindex >= 1:
                    file_name = match.group(1).strip()
                    if file_name:
                        # Normalize: if we have both "UserService" and "UserService.cs",
                        # keep only the .cs version
                        base_name = file_name.split('.')[0]
                        lower_key = base_name.lower()
                        
                        # Prefer file with extension
                        if '.' in file_name:
                            files_lower_map[lower_key] = file_name
                            files_set.add(file_name)
                        elif lower_key not in files_lower_map:
                            files_lower_map[lower_key] = file_name
                            files_set.add(file_name)
        
        entities.files = sorted(list(files_set))
        
        # Extract services
        services_set: Set[str] = set()
        for pattern in self.service_patterns:
            matches = re.finditer(pattern, requirements_text)
            for match in matches:
                if match.lastindex and match.lastindex >= 1:
                    service_name = match.group(1).strip()
                    if service_name:
                        # Clean up " for authentication" suffixes
                        service_name = re.sub(r'\s+for\s+\w+$', '', service_name)
                        services_set.add(service_name)
        
        entities.services = sorted(list(services_set))
        
        # Extract dependencies
        dependencies_set: Set[str] = set()
        for pattern in self.dependency_patterns:
            matches = re.finditer(pattern, requirements_text)
            for match in matches:
                if match.lastindex and match.lastindex >= 1:
                    dep_name = match.group(1).strip()
                    if dep_name:
                        dependencies_set.add(dep_name)
        
        entities.dependencies = sorted(list(dependencies_set))
        
        logger.info(f"Extracted entities: {len(entities.tables)} tables, "
                   f"{len(entities.files)} files, {len(entities.services)} services, "
                   f"{len(entities.dependencies)} dependencies")
        
        return entities
    
    def _normalize_entity_name(self, name: str) -> str:
        """Normalize entity names for deduplication (case-insensitive)"""
        name = name.strip()
        
        # Convert hyphens to underscores for consistency
        if '-' in name:
            name = name.replace('-', '_')
        
        # For underscore names, preserve original format
        if '_' in name:
            # Keep underscore format as-is (user_accounts stays user_accounts)
            return name
        
        # For other names, capitalize first letter only for consistency
        return name[0].upper() + name[1:] if name else name
    
    def calculate_confidence(self, entities: ScopeEntities, requirements_text: str = "") -> float:
        """
        Calculate confidence score based on entity clarity and completeness
        
        Confidence factors:
        - Explicit entity names (high confidence)
        - Quantified scope "15 tables" (high confidence)
        - Vague references "some tables" (low confidence)
        - Empty entities (low confidence)
        
        Args:
            entities: Extracted entities
            requirements_text: Original requirements (optional, for vague keyword detection)
        
        Returns:
            Confidence score (0.0-1.0)
        """
        score = 0.0
        max_score = 100.0
        
        # Tables confidence (40% weight) - 3+ tables = high confidence
        if entities.tables:
            # Scale: 1 table = 13%, 2 tables = 27%, 3 tables = 40%
            table_confidence = min(len(entities.tables) / 3.0, 1.0) * 40
            # Ensure 3+ tables gets full 40%
            if len(entities.tables) >= 3:
                table_confidence = 40
            score += table_confidence
        
        # Files confidence (30% weight) - 2+ files = high confidence
        if entities.files:
            # Scale: 1 file = 15%, 2 files = 30%
            file_confidence = min(len(entities.files) / 2.0, 1.0) * 30
            if len(entities.files) >= 2:
                file_confidence = 30
            score += file_confidence
        
        # Services confidence (20% weight) - 2+ services = high confidence
        if entities.services:
            # Scale: 1 service = 10%, 2 services = 20%
            service_confidence = min(len(entities.services) / 2.0, 1.0) * 20
            if len(entities.services) >= 2:
                service_confidence = 20
            score += service_confidence
        
        # Dependencies confidence (10% weight) - 2+ deps = high confidence
        if entities.dependencies:
            # Scale: 1 dep = 5%, 2+ deps = 10%
            dep_confidence = min(len(entities.dependencies) / 2.0, 1.0) * 10
            if len(entities.dependencies) >= 2:
                dep_confidence = 10
            score += dep_confidence
        
        # Check for vague keywords penalty
        if requirements_text and self._contains_vague_keywords(requirements_text):
            # Ensure vague requirements stay in medium confidence range (0.30-0.70)
            # If we extracted some entities but text is vague, cap at 0.60
            if score > 0:
                final_score = max(0.35, min(score / max_score, 0.60))
            else:
                final_score = 0.35  # Some entities detected, but vague
        else:
            # Normalize to 0-1 scale
            final_score = score / max_score
        
        logger.info(f"Confidence score: {final_score:.2f} "
                   f"(tables: {len(entities.tables)}, files: {len(entities.files)}, "
                   f"services: {len(entities.services)}, deps: {len(entities.dependencies)})")
        
        return final_score
    
    def generate_scope_boundary(self, entities: ScopeEntities, confidence: float) -> ScopeBoundary:
        """
        Create scope boundary with safety limits
        
        Args:
            entities: Detected entities
            confidence: Calculated confidence score (0.0-1.0)
            
        Returns:
            ScopeBoundary with counts, complexity estimate, and gaps
        """
        table_count = len(entities.tables)
        file_count = len(entities.files)
        service_count = len(entities.services)
        
        gaps = []
        
        # Enforce table limit (enterprise monolith protection)
        if table_count > self.MAX_TABLES:
            gaps.append(f"Scope exceeds {self.MAX_TABLES} table limit (detected {table_count}). "
                       f"Prioritization required.")
            table_count = self.MAX_TABLES
        
        # Enforce file limit
        if file_count > self.MAX_FILES:
            gaps.append(f"Scope exceeds {self.MAX_FILES} file limit (detected {file_count}). "
                       f"Prioritization required.")
            file_count = self.MAX_FILES
        
        # Identify gaps for clarification
        if confidence < self.HIGH_CONFIDENCE:
            if table_count == 0:
                gaps.append("No database tables mentioned. What tables will be affected?")
            if file_count == 0:
                gaps.append("No code files mentioned. What files will be modified?")
            if service_count == 0 and len(entities.dependencies) == 0:
                gaps.append("No external dependencies mentioned. Are there any integrations?")
        
        # Estimate complexity (0-100 scale)
        # Factors: table count, file count, service count, dependencies
        complexity = 0.0
        complexity += min(table_count / 20.0, 1.0) * 30  # 30% weight
        complexity += min(file_count / 30.0, 1.0) * 35  # 35% weight
        complexity += min(service_count / 5.0, 1.0) * 20  # 20% weight
        complexity += min(len(entities.dependencies) / 6.0, 1.0) * 15  # 15% weight
        
        boundary = ScopeBoundary(
            table_count=table_count,
            file_count=file_count,
            service_count=service_count,
            dependency_depth=self.MAX_DEPENDENCY_DEPTH,
            estimated_complexity=complexity,
            confidence=confidence,
            gaps=gaps
        )
        
        logger.info(f"Generated scope boundary: {table_count} tables, {file_count} files, "
                   f"{service_count} services, complexity: {complexity:.1f}, "
                   f"confidence: {confidence:.2f}, gaps: {len(gaps)}")
        
        return boundary


if __name__ == "__main__":
    # Quick test
    engine = ScopeInferenceEngine()
    test_requirements = """
    This feature implements user authentication:
    - Users table (add password_hash, salt)
    - Sessions table (new)
    - UserService.cs (authentication methods)
    - AuthController.cs (endpoints)
    - Azure AD for SSO
    - SendGrid for emails
    Requires OAuth 2.0 and JWT
    """
    
    entities = engine.extract_entities(test_requirements)
    confidence = engine.calculate_confidence(entities)
    boundary = engine.generate_scope_boundary(entities, confidence)
    
    print(f"Entities: {entities}")
    print(f"Confidence: {confidence:.2f}")
    print(f"Boundary: {boundary}")
