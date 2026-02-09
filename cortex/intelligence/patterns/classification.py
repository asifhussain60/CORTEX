# AC_START: AC-PHASE57-S3-002
# Description: Architecture Classification Engine
# Authority: CORE-008 TDD, CORE-011 type hints, CORE-012 docstrings
# Stage: S3 - GREEN phase implementation

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from enum import Enum

from cortex.intelligence.patterns.base import PatternMatch


class ArchitectureType(Enum):
    """Architecture pattern types."""
    MVC = "MVC"
    MVVM = "MVVM"
    DDD = "DDD"
    LAYERED = "Layered"
    MICROSERVICES = "Microservices"
    EVENT_DRIVEN = "EventDriven"
    CQRS = "CQRS"
    UNKNOWN = "Unknown"


@dataclass
class ArchitectureClassification:
    """Result of architecture classification."""
    type: str
    confidence: float
    patterns: List[str] = field(default_factory=list)
    reasoning: str = ""
    
    def __post_init__(self):
        """Validate classification data."""
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError(f"Confidence must be 0.0-1.0, got {self.confidence}")


class ArchitectureClassifier:
    """
    Classify architecture types based on detected patterns.
    
    Recognizes 7+ architecture types:
    - MVC/MVVM (Model-View-Controller/ViewModel)
    - DDD (Domain-Driven Design)
    - Layered (N-tier architecture)
    - Microservices
    - Event-Driven
    - CQRS (Command Query Responsibility Segregation)
    """

    def __init__(self):
        """Initialize ArchitectureClassifier with pattern signatures."""
        self.mvc_signatures = ["Model", "View", "Controller"]
        self.mvvm_signatures = ["Model", "ViewModel", "View"]
        self.ddd_signatures = ["AggregateRoot", "DomainEvent", "Repository"]
        self.layered_signatures = ["Facade", "ServiceLayer", "DataAccessLayer"]
        self.microservices_signatures = ["ServiceRegistry", "APIGateway", "CircuitBreaker"]
        self.event_driven_signatures = ["EventProducer", "EventConsumer", "EventBroker"]
        self.cqrs_signatures = ["CommandModel", "QueryModel", "EventStore"]

    def classify_architecture(
        self, 
        patterns: List[PatternMatch]
    ) -> Dict[str, any]:
        """
        Classify architecture based on detected patterns.
        
        Args:
            patterns: List of detected PatternMatch objects
            
        Returns:
            Dictionary with type, confidence, patterns, reasoning
            
        Raises:
            ValueError: If patterns list is invalid
        """
        if not patterns:
            return {
                "type": "Unknown",
                "confidence": 0.0,
                "patterns": [],
                "reasoning": "No patterns detected"
            }

        # Extract pattern names
        pattern_names = [p.pattern_name for p in patterns]
        
        # Check architectures in order of specificity
        classifications = []
        
        # Check CQRS (most specific)
        score = self._score_match(pattern_names, self.cqrs_signatures)
        if score > 0.0:
            classifications.append((ArchitectureType.CQRS.value, score))
        
        # Check DDD
        score = self._score_match(pattern_names, self.ddd_signatures)
        if score > 0.0:
            classifications.append((ArchitectureType.DDD.value, score))
        
        # Check Microservices
        score = self._score_match(pattern_names, self.microservices_signatures)
        if score > 0.0:
            classifications.append((ArchitectureType.MICROSERVICES.value, score))
        
        # Check Event-Driven
        score = self._score_match(pattern_names, self.event_driven_signatures)
        if score > 0.0:
            classifications.append((ArchitectureType.EVENT_DRIVEN.value, score))
        
        # Check Layered
        score = self._score_match(pattern_names, self.layered_signatures)
        if score > 0.0:
            classifications.append((ArchitectureType.LAYERED.value, score))
        
        # Check MVC
        score = self._score_match(pattern_names, self.mvc_signatures)
        if score > 0.0:
            classifications.append((ArchitectureType.MVC.value, score))
        
        # Check MVVM
        score = self._score_match(pattern_names, self.mvvm_signatures)
        if score > 0.0:
            classifications.append((ArchitectureType.MVVM.value, score))
        
        # Get highest scoring classification
        if classifications:
            arch_type, confidence = max(classifications, key=lambda x: x[1])
        else:
            arch_type = "Unknown"
            confidence = 0.0
        
        return {
            "type": arch_type,
            "confidence": confidence,
            "patterns": pattern_names,
            "reasoning": self._generate_reasoning(arch_type, pattern_names)
        }

    def _score_match(self, detected: List[str], signatures: List[str]) -> float:
        """
        Score how well detected patterns match architecture signatures.
        
        Args:
            detected: List of detected pattern names
            signatures: List of signature patterns for architecture
            
        Returns:
            Confidence score (0.0-1.0) based on pattern matches
        """
        if not signatures:
            return 0.0
        
        matches = sum(1 for sig in signatures if sig in detected)
        return matches / len(signatures)

    def _generate_reasoning(self, arch_type: str, patterns: List[str]) -> str:
        """Generate reasoning text for classification."""
        if arch_type == "Unknown":
            return "Insufficient pattern matches to classify"
        return f"Classified as {arch_type} based on detected patterns: {', '.join(patterns[:3])}"

# AC_COMPLETE: AC-PHASE57-S3-002 ✅
# Implementation: ArchitectureClassifier with 7 architecture types
# Status: READY FOR TESTING
