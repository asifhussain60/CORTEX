"""
Problem Domain Narrator - Explain what problem the application solves

Synthesizes "What problem does this solve?" narratives from:
- Code comments with business context
- Entity relationships and domain models
- Regulatory/compliance keywords
- Common pain points by domain

Example:
    Input: Healthcare app with Patient, Provider, Claim entities
    Output: "Coordinates healthcare provider reimbursement, reducing claim
            processing time from weeks to days while ensuring compliance
            with HIPAA and insurance regulations."

Author: Asif Hussain
"""

from typing import Dict, Any, List, Optional, Set
import re
import logging

logger = logging.getLogger(__name__)


class ProblemDomainNarrator:
    """
    Narrates what business problem the application solves.
    
    Analyzes code structure, comments, and entity relationships to synthesize
    a business-focused problem statement that non-technical stakeholders
    can understand.
    
    Strategy:
        1. Extract domain entities (classes, models, tables)
        2. Identify relationships and business rules
        3. Search comments for problem/solution keywords
        4. Detect regulatory/compliance requirements
        5. Map to common business problem patterns
        6. Generate problem statement + solution + benefits
    
    Example:
        >>> narrator = ProblemDomainNarrator()
        >>> problem = narrator.narrate({
        ...     'architecture': {'entities': ['Order', 'Customer', 'Payment']},
        ...     'comments': {'business_comments': [...]}
        ... })
        >>> print(problem['problem_statement'])
        'Manual order processing causes delays and errors...'
    """
    
    # Common business problem patterns
    PROBLEM_PATTERNS = {
        'workflow_automation': {
            'keywords': ['manual', 'automate', 'streamline', 'process', 'workflow'],
            'problem': 'Manual processes are slow, error-prone, and do not scale',
            'solution_verb': 'Automates'
        },
        'data_consolidation': {
            'keywords': ['consolidate', 'integrate', 'centralize', 'unified', 'single source'],
            'problem': 'Data is scattered across multiple systems causing inefficiency',
            'solution_verb': 'Consolidates'
        },
        'compliance': {
            'keywords': ['compliance', 'regulatory', 'audit', 'gdpr', 'hipaa', 'sox'],
            'problem': 'Regulatory compliance is complex and risky',
            'solution_verb': 'Ensures compliance with'
        },
        'customer_experience': {
            'keywords': ['customer', 'user experience', 'self-service', 'portal'],
            'problem': 'Customers lack visibility and control',
            'solution_verb': 'Empowers customers with'
        },
        'analytics': {
            'keywords': ['analytics', 'insights', 'reporting', 'dashboard', 'metrics'],
            'problem': 'Decision-makers lack actionable insights',
            'solution_verb': 'Provides real-time insights into'
        }
    }
    
    # Domain-specific problem templates
    DOMAIN_TEMPLATES = {
        'healthcare': {
            'problem': 'Healthcare providers struggle with complex reimbursement processes',
            'impact': 'Delayed payments, administrative burden, compliance risk'
        },
        'finance': {
            'problem': 'Financial operations require manual reconciliation and reporting',
            'impact': 'Errors, audit failures, slow month-end close'
        },
        'ecommerce': {
            'problem': 'Online businesses need efficient order and inventory management',
            'impact': 'Lost sales, customer dissatisfaction, operational inefficiency'
        },
        'logistics': {
            'problem': 'Supply chain visibility and coordination is fragmented',
            'impact': 'Delays, excess inventory, customer service issues'
        }
    }
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize problem domain narrator with optional configuration."""
        self.config = config or {}
        logger.info("🎯 ProblemDomainNarrator initialized")
    
    def narrate(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate problem domain narrative from analysis data.
        
        Args:
            analysis_data: Complete analysis with architecture, comments, tech_stack
        
        Returns:
            Dictionary with:
                - problem_statement: What problem exists
                - solution_description: How the app solves it
                - stakeholder_benefits: Who benefits and how
                - domain: Business domain (healthcare, finance, etc.)
                - evidence: Code-based evidence
        """
        logger.info("🎯 Generating problem domain narrative")
        
        # Extract entities and domain
        entities = self._extract_entities(analysis_data)
        domain = self._detect_domain(entities, analysis_data)
        
        # Analyze comments for business context
        business_context = self._extract_business_context(analysis_data)
        
        # Detect problem pattern
        problem_pattern = self._detect_problem_pattern(business_context, entities)
        
        # Generate narrative
        narrative = {
            'domain': domain,
            'problem_statement': self._generate_problem_statement(domain, problem_pattern, entities),
            'solution_description': self._generate_solution(domain, problem_pattern, entities),
            'stakeholder_benefits': self._generate_benefits(domain, entities),
            'evidence': {
                'entities': entities[:10],  # Top 10 entities
                'entity_count': len(entities),
                'business_comment_count': len(business_context),
                'detected_patterns': [problem_pattern] if problem_pattern else []
            }
        }
        
        logger.info(f"✅ Generated problem domain narrative for {domain}")
        return narrative
    
    def _extract_entities(self, data: Dict[str, Any]) -> List[str]:
        """Extract business entities from code (classes, models, tables)."""
        entities = []
        
        # From architecture collector
        arch = data.get('architecture', {})
        entities.extend(arch.get('entities', []))
        
        # From database schema if available
        db_schema = data.get('database_schema', {})
        entities.extend(db_schema.get('tables', []))
        
        # From Python class analysis
        # (Would integrate with existing analyzers)
        
        return list(set(entities))  # Deduplicate
    
    def _detect_domain(self, entities: List[str], data: Dict[str, Any]) -> str:
        """
        Detect business domain from entities and tech stack.
        
        Uses entity names and technology choices to classify domain:
        - Patient, Provider, Claim -> healthcare
        - Order, Customer, Payment -> ecommerce
        - Account, Transaction, Ledger -> finance
        """
        entity_text = ' '.join(entities).lower()
        
        # Healthcare indicators
        if any(kw in entity_text for kw in ['patient', 'provider', 'claim', 'diagnosis', 'medical']):
            return 'healthcare'
        
        # Finance indicators
        if any(kw in entity_text for kw in ['account', 'transaction', 'ledger', 'invoice', 'payment']):
            return 'finance'
        
        # E-commerce indicators
        if any(kw in entity_text for kw in ['order', 'product', 'cart', 'checkout', 'inventory']):
            return 'ecommerce'
        
        # Logistics indicators
        if any(kw in entity_text for kw in ['shipment', 'warehouse', 'delivery', 'tracking']):
            return 'logistics'
        
        return 'general'
    
    def _extract_business_context(self, data: Dict[str, Any]) -> List[str]:
        """Extract business-focused comments from code."""
        comments = data.get('comments', {})
        business_comments = []
        
        # Filter for comments with business keywords
        business_keywords = [
            'business', 'requirement', 'workflow', 'process', 'rule',
            'compliance', 'regulation', 'customer', 'user', 'stakeholder'
        ]
        
        all_comments = comments.get('all_comments', [])
        for comment in all_comments:
            text = comment.get('text', '').lower()
            if any(kw in text for kw in business_keywords):
                business_comments.append(comment.get('text', ''))
        
        return business_comments
    
    def _detect_problem_pattern(
        self,
        business_context: List[str],
        entities: List[str]
    ) -> Optional[str]:
        """Detect which problem pattern this application addresses."""
        context_text = ' '.join(business_context).lower()
        entity_text = ' '.join(entities).lower()
        combined = context_text + ' ' + entity_text
        
        # Score each pattern
        scores = {}
        for pattern_name, pattern_info in self.PROBLEM_PATTERNS.items():
            score = sum(1 for kw in pattern_info['keywords'] if kw in combined)
            if score > 0:
                scores[pattern_name] = score
        
        # Return highest scoring pattern
        if scores:
            return max(scores.items(), key=lambda x: x[1])[0]
        return None
    
    def _generate_problem_statement(
        self,
        domain: str,
        problem_pattern: Optional[str],
        entities: List[str]
    ) -> str:
        """Generate problem statement."""
        # Use domain template if available
        if domain in self.DOMAIN_TEMPLATES:
            return self.DOMAIN_TEMPLATES[domain]['problem']
        
        # Use pattern template
        if problem_pattern and problem_pattern in self.PROBLEM_PATTERNS:
            return self.PROBLEM_PATTERNS[problem_pattern]['problem']
        
        # Generic statement based on entities
        if len(entities) > 3:
            return f"Organizations need to manage complex {', '.join(entities[:3])} operations efficiently"
        
        return "Organizations face operational challenges that require automation"
    
    def _generate_solution(
        self,
        domain: str,
        problem_pattern: Optional[str],
        entities: List[str]
    ) -> str:
        """Generate solution description."""
        verb = "Provides"
        if problem_pattern and problem_pattern in self.PROBLEM_PATTERNS:
            verb = self.PROBLEM_PATTERNS[problem_pattern]['solution_verb']
        
        if len(entities) > 2:
            entity_list = ', '.join(entities[:3])
            return f"{verb} integrated management of {entity_list} with automated workflows and real-time visibility"
        
        return f"{verb} a comprehensive platform for {domain} operations"
    
    def _generate_benefits(self, domain: str, entities: List[str]) -> List[Dict[str, str]]:
        """Generate stakeholder benefits."""
        benefits = []
        
        # Domain-specific benefits
        if domain == 'healthcare':
            benefits.extend([
                {'stakeholder': 'Healthcare Providers', 'benefit': 'Faster reimbursement, reduced administrative burden'},
                {'stakeholder': 'Patients', 'benefit': 'Improved care coordination, faster service'},
                {'stakeholder': 'Administrators', 'benefit': 'Compliance assurance, audit readiness'}
            ])
        elif domain == 'finance':
            benefits.extend([
                {'stakeholder': 'Finance Team', 'benefit': 'Faster month-end close, reduced errors'},
                {'stakeholder': 'Auditors', 'benefit': 'Complete audit trail, compliance evidence'},
                {'stakeholder': 'Executives', 'benefit': 'Real-time financial visibility'}
            ])
        elif domain == 'ecommerce':
            benefits.extend([
                {'stakeholder': 'Customers', 'benefit': 'Faster checkout, real-time order tracking'},
                {'stakeholder': 'Operations', 'benefit': 'Inventory optimization, reduced fulfillment time'},
                {'stakeholder': 'Business Owners', 'benefit': 'Increased sales, lower operational costs'}
            ])
        else:
            # Generic benefits
            benefits.extend([
                {'stakeholder': 'End Users', 'benefit': 'Improved productivity, reduced manual work'},
                {'stakeholder': 'Managers', 'benefit': 'Better visibility, data-driven decisions'},
                {'stakeholder': 'Organization', 'benefit': 'Operational efficiency, competitive advantage'}
            ])
        
        return benefits
