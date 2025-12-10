"""
Financial Data Detector for Intelligent Dashboard

Identifies financial code patterns, PCI/SOX compliance markers.

Features:
- Currency pattern detection
- Financial entity recognition (Account, Transaction, Payment)
- Calculation flow tracing
- PCI/SOX compliance markers
- Risk scoring

Author: Asif Hussain
Date: December 10, 2025
"""

from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass
from enum import Enum
import re
import logging

logger = logging.getLogger(__name__)


class FinancialEntityType(Enum):
    """Financial entity types."""
    ACCOUNT = "account"
    TRANSACTION = "transaction"
    PAYMENT = "payment"
    INVOICE = "invoice"
    CARD = "card"
    WALLET = "wallet"


class ComplianceStandard(Enum):
    """Compliance standards."""
    PCI_DSS = "pci_dss"
    SOX = "sox"
    GDPR = "gdpr"
    NONE = "none"


class RiskLevel(Enum):
    """Risk levels for financial code."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class FinancialPattern:
    """Financial pattern detected in code."""
    pattern_type: str
    location: str
    confidence: float
    risk_level: RiskLevel
    description: str


@dataclass
class FinancialEntity:
    """Financial entity (class) detected."""
    entity_type: FinancialEntityType
    class_name: str
    location: str
    attributes: List[str]
    methods: List[str]


@dataclass
class ComplianceMarker:
    """PCI/SOX compliance marker."""
    standard: ComplianceStandard
    location: str
    description: str
    risk_level: RiskLevel


class FinancialDataDetector:
    """
    Detects financial code patterns and compliance markers.
    
    Detection Methods:
    1. Currency pattern matching (regex + AST)
    2. Financial entity recognition (class analysis)
    3. Calculation flow tracing (AST traversal)
    4. Compliance marker identification
    """
    
    # Currency patterns
    CURRENCY_SYMBOLS = ['$', '€', '£', '¥', '₹']
    CURRENCY_CODES = ['USD', 'EUR', 'GBP', 'JPY', 'INR', 'CAD', 'AUD']
    CURRENCY_KEYWORDS = ['currency', 'price', 'amount', 'cost', 'fee', 'charge']
    
    # Financial keywords
    FINANCIAL_KEYWORDS = {
        'account', 'transaction', 'payment', 'invoice', 'balance',
        'credit', 'debit', 'transfer', 'refund', 'charge',
        'interest', 'principal', 'loan', 'deposit', 'withdrawal'
    }
    
    # PCI/SOX keywords
    PCI_KEYWORDS = {
        'card_number', 'cvv', 'expiry', 'pan', 'cardholder',
        'encrypt', 'decrypt', 'tokenize', 'mask'
    }
    
    SOX_KEYWORDS = {
        'audit', 'financial_report', 'disclosure', 'internal_control',
        'segregation_of_duties', 'compliance'
    }
    
    def __init__(self):
        """Initialize financial data detector."""
        self.patterns_found = 0
        self.entities_found = 0
        self.compliance_markers_found = 0
    
    def detect_financial_patterns(
        self,
        ast_tree: Any,
        source_code: str,
        file_path: str
    ) -> List[FinancialPattern]:
        """
        Detect financial patterns in code.
        
        Args:
            ast_tree: Tree-sitter AST tree
            source_code: Original source code
            file_path: File path for location tracking
            
        Returns:
            List of FinancialPattern objects
        """
        patterns = []
        
        # Detect currency patterns
        patterns.extend(self._detect_currency_patterns(source_code, file_path))
        
        # Detect decimal patterns (financial amounts)
        patterns.extend(self._detect_decimal_patterns(source_code, file_path))
        
        self.patterns_found += len(patterns)
        return patterns
    
    def detect_financial_entities(
        self,
        ast_tree: Any,
        source_code: str,
        file_path: str
    ) -> List[FinancialEntity]:
        """
        Detect financial entities (classes).
        
        Args:
            ast_tree: Tree-sitter AST tree
            source_code: Original source code
            file_path: File path for location tracking
            
        Returns:
            List of FinancialEntity objects
        """
        entities = []
        
        # Detect class definitions with financial names
        entities.extend(self._detect_entity_classes(source_code, file_path))
        
        self.entities_found += len(entities)
        return entities
    
    def detect_compliance_markers(
        self,
        ast_tree: Any,
        source_code: str,
        file_path: str
    ) -> List[ComplianceMarker]:
        """
        Detect PCI/SOX compliance markers.
        
        Args:
            ast_tree: Tree-sitter AST tree
            source_code: Original source code
            file_path: File path for location tracking
            
        Returns:
            List of ComplianceMarker objects
        """
        markers = []
        
        # Detect PCI markers
        markers.extend(self._detect_pci_markers(source_code, file_path))
        
        # Detect SOX markers
        markers.extend(self._detect_sox_markers(source_code, file_path))
        
        self.compliance_markers_found += len(markers)
        return markers
    
    def _detect_currency_patterns(
        self,
        source_code: str,
        file_path: str
    ) -> List[FinancialPattern]:
        """Detect currency symbols and codes."""
        patterns = []
        lines = source_code.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            # Check for currency symbols
            for symbol in self.CURRENCY_SYMBOLS:
                if symbol in line:
                    patterns.append(FinancialPattern(
                        pattern_type="currency_symbol",
                        location=f"{file_path}:{line_num}",
                        confidence=0.90,
                        risk_level=RiskLevel.MEDIUM,
                        description=f"Currency symbol '{symbol}' detected"
                    ))
            
            # Check for currency codes
            for code in self.CURRENCY_CODES:
                if code in line:
                    patterns.append(FinancialPattern(
                        pattern_type="currency_code",
                        location=f"{file_path}:{line_num}",
                        confidence=0.85,
                        risk_level=RiskLevel.LOW,
                        description=f"Currency code '{code}' detected"
                    ))
        
        return patterns
    
    def _detect_decimal_patterns(
        self,
        source_code: str,
        file_path: str
    ) -> List[FinancialPattern]:
        """Detect decimal number patterns (potential financial amounts)."""
        patterns = []
        lines = source_code.split('\n')
        
        # Pattern for decimal numbers with 2 decimal places (common for currency)
        decimal_pattern = r'\b\d+\.\d{2}\b'
        
        for line_num, line in enumerate(lines, 1):
            # Check if line contains financial keywords
            if any(kw in line.lower() for kw in self.CURRENCY_KEYWORDS):
                matches = re.findall(decimal_pattern, line)
                if matches:
                    patterns.append(FinancialPattern(
                        pattern_type="decimal_amount",
                        location=f"{file_path}:{line_num}",
                        confidence=0.75,
                        risk_level=RiskLevel.LOW,
                        description=f"Financial amount pattern detected: {matches[0]}"
                    ))
        
        return patterns
    
    def _detect_entity_classes(
        self,
        source_code: str,
        file_path: str
    ) -> List[FinancialEntity]:
        """Detect financial entity classes."""
        entities = []
        lines = source_code.split('\n')
        
        # Pattern for class definitions
        class_pattern = r'class\s+(\w+)'
        
        for line_num, line in enumerate(lines, 1):
            match = re.search(class_pattern, line)
            if match:
                class_name = match.group(1)
                class_name_lower = class_name.lower()
                
                # Check if class name contains financial keywords
                entity_type = None
                for keyword in self.FINANCIAL_KEYWORDS:
                    if keyword in class_name_lower:
                        # Map keyword to entity type
                        if 'account' in class_name_lower:
                            entity_type = FinancialEntityType.ACCOUNT
                        elif 'transaction' in class_name_lower:
                            entity_type = FinancialEntityType.TRANSACTION
                        elif 'payment' in class_name_lower:
                            entity_type = FinancialEntityType.PAYMENT
                        elif 'invoice' in class_name_lower:
                            entity_type = FinancialEntityType.INVOICE
                        elif 'card' in class_name_lower:
                            entity_type = FinancialEntityType.CARD
                        elif 'wallet' in class_name_lower:
                            entity_type = FinancialEntityType.WALLET
                        break
                
                if entity_type:
                    # Extract attributes and methods (simplified)
                    attributes = self._extract_class_attributes(lines, line_num)
                    methods = self._extract_class_methods(lines, line_num)
                    
                    entities.append(FinancialEntity(
                        entity_type=entity_type,
                        class_name=class_name,
                        location=f"{file_path}:{line_num}",
                        attributes=attributes,
                        methods=methods
                    ))
        
        return entities
    
    def _extract_class_attributes(self, lines: List[str], class_line: int) -> List[str]:
        """Extract class attributes (simplified)."""
        attributes = []
        
        # Look at next 20 lines for self.attribute assignments
        for i in range(class_line, min(class_line + 20, len(lines))):
            line = lines[i].strip()
            match = re.search(r'self\.(\w+)\s*=', line)
            if match:
                attributes.append(match.group(1))
        
        return attributes[:10]  # Limit to 10
    
    def _extract_class_methods(self, lines: List[str], class_line: int) -> List[str]:
        """Extract class methods (simplified)."""
        methods = []
        
        # Look at next 50 lines for method definitions
        for i in range(class_line, min(class_line + 50, len(lines))):
            line = lines[i].strip()
            match = re.search(r'def\s+(\w+)\s*\(', line)
            if match:
                method_name = match.group(1)
                if not method_name.startswith('_'):  # Skip private methods
                    methods.append(method_name)
        
        return methods[:10]  # Limit to 10
    
    def _detect_pci_markers(
        self,
        source_code: str,
        file_path: str
    ) -> List[ComplianceMarker]:
        """Detect PCI DSS compliance markers."""
        markers = []
        lines = source_code.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            line_lower = line.lower()
            
            for keyword in self.PCI_KEYWORDS:
                if keyword in line_lower:
                    # Determine risk level
                    if 'card_number' in line_lower or 'cvv' in line_lower:
                        risk = RiskLevel.CRITICAL
                    elif 'encrypt' in line_lower or 'tokenize' in line_lower:
                        risk = RiskLevel.MEDIUM
                    else:
                        risk = RiskLevel.HIGH
                    
                    markers.append(ComplianceMarker(
                        standard=ComplianceStandard.PCI_DSS,
                        location=f"{file_path}:{line_num}",
                        description=f"PCI DSS sensitive code detected: {keyword}",
                        risk_level=risk
                    ))
                    break  # One marker per line
        
        return markers
    
    def _detect_sox_markers(
        self,
        source_code: str,
        file_path: str
    ) -> List[ComplianceMarker]:
        """Detect SOX compliance markers."""
        markers = []
        lines = source_code.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            line_lower = line.lower()
            
            for keyword in self.SOX_KEYWORDS:
                if keyword in line_lower:
                    markers.append(ComplianceMarker(
                        standard=ComplianceStandard.SOX,
                        location=f"{file_path}:{line_num}",
                        description=f"SOX compliance code detected: {keyword}",
                        risk_level=RiskLevel.MEDIUM
                    ))
                    break  # One marker per line
        
        return markers
    
    def get_statistics(self) -> Dict[str, int]:
        """Get detection statistics."""
        return {
            'patterns_found': self.patterns_found,
            'entities_found': self.entities_found,
            'compliance_markers_found': self.compliance_markers_found
        }
