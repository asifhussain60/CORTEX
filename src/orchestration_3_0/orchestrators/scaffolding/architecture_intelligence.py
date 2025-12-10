"""
Architecture Intelligence Component
Pattern recognition and modern architecture recommendations.

Features:
- Recognizes architectural patterns (MVC, monolith, microservices)
- Recommends modern replacements (Clean Architecture, DDD, microservices)
- Identifies service decomposition boundaries
- Suggests technology stack upgrades
"""

from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, asdict
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ArchitecturalPattern(Enum):
    """Known architectural patterns."""
    MVC_MONOLITH = "mvc_monolith"
    LAYERED_MONOLITH = "layered_monolith"
    SPAGHETTI_CODE = "spaghetti_code"
    PROCEDURAL = "procedural"
    MICROSERVICES = "microservices"
    CLEAN_ARCHITECTURE = "clean_architecture"
    DOMAIN_DRIVEN_DESIGN = "ddd"
    HEXAGONAL = "hexagonal"
    UNKNOWN = "unknown"


@dataclass
class ServiceCandidate:
    """Potential service for microservices decomposition."""
    name: str
    files: List[str]
    confidence: float
    rationale: str


@dataclass
class ArchitectureAssessment:
    """Complete architecture analysis and recommendations."""
    current_pattern: str
    current_confidence: float
    recommended_pattern: str
    rationale: str
    layers: Dict[str, List[str]]
    service_candidates: List[ServiceCandidate]
    tech_stack: Dict[str, str]


class ArchitectureIntelligence:
    """
    Recognizes architectural patterns and recommends modern replacements.
    
    Analyzes code structure report from CodeAnalyzer and identifies:
    - Current architectural pattern
    - Recommended target pattern
    - Layer boundaries
    - Service decomposition candidates
    - Technology stack recommendations
    
    Example:
        intelligence = ArchitectureIntelligence()
        assessment = intelligence.assess(code_report, constraints={"target": "microservices"})
        print(f"Recommended: {assessment.recommended_pattern}")
    """
    
    # Pattern confidence thresholds
    HIGH_CONFIDENCE = 0.8
    MEDIUM_CONFIDENCE = 0.6
    
    def __init__(self):
        """Initialize architecture intelligence engine."""
        self.pattern_indicators = self._build_pattern_indicators()
        self.modernization_map = self._build_modernization_map()
    
    def assess(self, code_report: Dict[str, Any], constraints: Optional[Dict[str, Any]] = None) -> ArchitectureAssessment:
        """
        Assess architecture and recommend improvements.
        
        Args:
            code_report: Code structure report from CodeAnalyzer
            constraints: User constraints (target_framework, cloud_platform, team_expertise)
        
        Returns:
            ArchitectureAssessment with recommendations
        """
        constraints = constraints or {}
        
        # Step 1: Recognize current pattern
        current_pattern, confidence = self._recognize_pattern(code_report)
        
        # Step 2: Recommend target pattern
        recommended_pattern = self._recommend_pattern(current_pattern, code_report, constraints)
        
        # Step 3: Identify layers
        layers = self._identify_layers(code_report, current_pattern)
        
        # Step 4: Find service candidates (if targeting microservices)
        service_candidates = []
        if recommended_pattern in [ArchitecturalPattern.MICROSERVICES.value, ArchitecturalPattern.CLEAN_ARCHITECTURE.value]:
            service_candidates = self._find_service_candidates(code_report)
        
        # Step 5: Recommend tech stack
        tech_stack = self._recommend_tech_stack(code_report, recommended_pattern, constraints)
        
        # Build assessment
        assessment = ArchitectureAssessment(
            current_pattern=current_pattern,
            current_confidence=confidence,
            recommended_pattern=recommended_pattern,
            rationale=self._generate_rationale(current_pattern, recommended_pattern),
            layers=layers,
            service_candidates=service_candidates,
            tech_stack=tech_stack
        )
        
        logger.info(f"Architecture assessment: {current_pattern} → {recommended_pattern} (confidence: {confidence:.2f})")
        return assessment
    
    def _build_pattern_indicators(self) -> Dict[ArchitecturalPattern, Dict[str, Any]]:
        """Build pattern recognition indicators."""
        return {
            ArchitecturalPattern.MVC_MONOLITH: {
                'framework_indicators': ['flask', 'django', 'express', 'rails'],
                'folder_indicators': ['views', 'controllers', 'models'],
                'min_modules': 10,
                'max_services': 1
            },
            ArchitecturalPattern.LAYERED_MONOLITH: {
                'folder_indicators': ['presentation', 'business', 'data', 'services'],
                'min_modules': 15,
                'max_services': 1
            },
            ArchitecturalPattern.SPAGHETTI_CODE: {
                'anti_pattern_count': 5,  # High anti-pattern count
                'avg_complexity': 50,  # High complexity
                'min_hotspots': 3
            },
            ArchitecturalPattern.CLEAN_ARCHITECTURE: {
                'folder_indicators': ['domain', 'application', 'infrastructure', 'presentation'],
                'min_modules': 20,
                'layer_separation': True
            },
            ArchitecturalPattern.MICROSERVICES: {
                'service_count': 2,  # Multiple services
                'api_gateway': True
            }
        }
    
    def _build_modernization_map(self) -> Dict[str, str]:
        """Build modernization recommendations map."""
        return {
            ArchitecturalPattern.MVC_MONOLITH.value: ArchitecturalPattern.CLEAN_ARCHITECTURE.value,
            ArchitecturalPattern.LAYERED_MONOLITH.value: ArchitecturalPattern.CLEAN_ARCHITECTURE.value,
            ArchitecturalPattern.SPAGHETTI_CODE.value: ArchitecturalPattern.LAYERED_MONOLITH.value,
            ArchitecturalPattern.PROCEDURAL.value: ArchitecturalPattern.DOMAIN_DRIVEN_DESIGN.value,
            ArchitecturalPattern.CLEAN_ARCHITECTURE.value: ArchitecturalPattern.MICROSERVICES.value,
        }
    
    def _recognize_pattern(self, code_report: Dict[str, Any]) -> tuple[str, float]:
        """Recognize current architectural pattern."""
        framework = (code_report.get('framework') or '').lower()
        modules = code_report.get('modules', 0)
        anti_patterns = code_report.get('anti_patterns', [])
        hotspots = code_report.get('hotspots', [])
        
        # Check MVC monolith
        mvc_indicators = self.pattern_indicators[ArchitecturalPattern.MVC_MONOLITH]
        if any(fw in framework for fw in mvc_indicators['framework_indicators']):
            if modules >= mvc_indicators['min_modules']:
                return ArchitecturalPattern.MVC_MONOLITH.value, self.HIGH_CONFIDENCE
        
        # Check spaghetti code (high anti-patterns + hotspots)
        spaghetti_indicators = self.pattern_indicators[ArchitecturalPattern.SPAGHETTI_CODE]
        if len(anti_patterns) >= spaghetti_indicators['anti_pattern_count'] and len(hotspots) >= spaghetti_indicators['min_hotspots']:
            return ArchitecturalPattern.SPAGHETTI_CODE.value, self.HIGH_CONFIDENCE
        
        # Check layered monolith (presence of layer folders)
        layered_indicators = self.pattern_indicators[ArchitecturalPattern.LAYERED_MONOLITH]
        if modules >= layered_indicators['min_modules']:
            return ArchitecturalPattern.LAYERED_MONOLITH.value, self.MEDIUM_CONFIDENCE
        
        # Default to procedural for small codebases
        if modules < 10:
            return ArchitecturalPattern.PROCEDURAL.value, self.MEDIUM_CONFIDENCE
        
        return ArchitecturalPattern.UNKNOWN.value, 0.5
    
    def _recommend_pattern(self, current_pattern: str, code_report: Dict[str, Any], constraints: Dict[str, Any]) -> str:
        """Recommend target architectural pattern."""
        # User override
        if 'target_pattern' in constraints:
            return constraints['target_pattern']
        
        # Use modernization map
        recommended = self.modernization_map.get(current_pattern, ArchitecturalPattern.CLEAN_ARCHITECTURE.value)
        
        # Adjust based on codebase size
        modules = code_report.get('modules', 0)
        if modules < 20 and recommended == ArchitecturalPattern.MICROSERVICES.value:
            # Too small for microservices
            recommended = ArchitecturalPattern.CLEAN_ARCHITECTURE.value
        
        return recommended
    
    def _identify_layers(self, code_report: Dict[str, Any], current_pattern: str) -> Dict[str, List[str]]:
        """Identify or recommend layer structure."""
        # For now, recommend Clean Architecture layers
        # In production, would analyze actual folder structure
        return {
            'presentation': ['controllers/', 'views/', 'api/'],
            'business_logic': ['services/', 'domain/', 'use_cases/'],
            'data_access': ['repositories/', 'models/', 'entities/'],
            'infrastructure': ['config/', 'utils/', 'middleware/']
        }
    
    def _find_service_candidates(self, code_report: Dict[str, Any]) -> List[ServiceCandidate]:
        """Identify candidates for service decomposition."""
        # Simplified: look for high-cohesion modules
        # In production, would use domain analysis and clustering algorithms
        
        candidates = []
        
        # Example: If "payment" appears in multiple files, suggest PaymentService
        file_keywords = ['payment', 'user', 'order', 'inventory', 'notification']
        
        for keyword in file_keywords:
            # Mock detection (in production, scan actual file names)
            if code_report.get('modules', 0) > 20:
                candidates.append(ServiceCandidate(
                    name=f"{keyword.capitalize()}Service",
                    files=[f"{keyword}.py", f"{keyword}_repository.py"],
                    confidence=0.75,
                    rationale=f"High cohesion around {keyword} domain"
                ))
        
        return candidates[:3]  # Top 3 candidates
    
    def _recommend_tech_stack(self, code_report: Dict[str, Any], recommended_pattern: str, constraints: Dict[str, Any]) -> Dict[str, str]:
        """Recommend modern technology stack."""
        language = code_report.get('language', 'python')
        
        # Python stack
        if language == 'python':
            return {
                'framework': constraints.get('target_framework', 'FastAPI'),
                'orm': 'SQLAlchemy',
                'testing': 'pytest + pytest-cov',
                'async': 'asyncio',
                'di': 'dependency-injector'
            }
        
        # JavaScript/TypeScript stack
        elif language in ['javascript', 'typescript']:
            return {
                'framework': constraints.get('target_framework', 'NestJS'),
                'orm': 'TypeORM',
                'testing': 'Jest',
                'async': 'async/await',
                'di': 'tsyringe'
            }
        
        # C# stack
        elif language == 'csharp':
            return {
                'framework': '.NET 8',
                'orm': 'Entity Framework Core',
                'testing': 'xUnit + Moq',
                'async': 'async/await',
                'di': 'Microsoft.Extensions.DependencyInjection'
            }
        
        return {}
    
    def _generate_rationale(self, current_pattern: str, recommended_pattern: str) -> str:
        """Generate human-readable rationale for recommendation."""
        rationale_map = {
            (ArchitecturalPattern.MVC_MONOLITH.value, ArchitecturalPattern.CLEAN_ARCHITECTURE.value):
                "Clean Architecture provides better separation of concerns, testability, and framework independence compared to traditional MVC",
            
            (ArchitecturalPattern.SPAGHETTI_CODE.value, ArchitecturalPattern.LAYERED_MONOLITH.value):
                "Layered architecture introduces structure and separation, making code more maintainable and reducing technical debt",
            
            (ArchitecturalPattern.CLEAN_ARCHITECTURE.value, ArchitecturalPattern.MICROSERVICES.value):
                "Microservices enable independent deployment, scaling, and team autonomy for mature Clean Architecture codebases",
        }
        
        return rationale_map.get((current_pattern, recommended_pattern), 
                                 f"Modernizing from {current_pattern} to {recommended_pattern} improves maintainability and scalability")
    
    def to_dict(self, assessment: ArchitectureAssessment) -> Dict[str, Any]:
        """Convert assessment to dictionary for JSON serialization."""
        return {
            **asdict(assessment),
            'service_candidates': [asdict(sc) for sc in assessment.service_candidates]
        }
