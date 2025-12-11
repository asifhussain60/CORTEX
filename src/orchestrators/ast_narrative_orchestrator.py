"""
AST-to-Narrative Orchestrator

Transforms Abstract Syntax Tree (AST) analysis data into business-focused textual narratives.
Synthesizes JSON data from code analysis into human-readable executive summaries and
contextual descriptions for dashboard integration.

Author: Asif Hussain
Copyright: © 2025 Asif Hussain. All rights reserved.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class NarrativeSection:
    """Represents a narrative section with metadata"""
    title: str
    content: str
    section_type: str  # executive, technical, business, compliance
    word_count: int
    data_sources: List[str]


@dataclass
class NarrativeRequest:
    """Request parameters for narrative generation"""
    analysis_path: Path  # Path to RA-Domain analysis-results/
    output_path: Path    # Where to save generated narrative
    narrative_type: str  # executive, technical, business_use_cases, compliance
    target_audience: str # leadership, developers, product_managers, auditors
    max_length: str     # brief (500 words), standard (1500 words), detailed (3000 words)


class ASTNarrativeOrchestrator:
    """
    Orchestrates the transformation of AST data into business narratives.
    
    Workflow:
    1. Data Aggregation - Load and consolidate JSON files
    2. Template Selection - Choose narrative template based on audience
    3. Synthesis - Generate narrative content (via Copilot or LLM)
    4. Assembly - Combine sections into final document
    5. Validation - Ensure quality and completeness
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
        self.narrative_sections: List[NarrativeSection] = []
        
    def generate_narrative(self, request: NarrativeRequest) -> Dict[str, Any]:
        """
        Main orchestration method for narrative generation.
        
        Args:
            request: NarrativeRequest with all generation parameters
            
        Returns:
            Dict with narrative content, metadata, and status
        """
        self.logger.info(f"🎭 Orchestrator engaged: ASTNarrativeOrchestrator")
        self.logger.info(f"   Type: {request.narrative_type}")
        self.logger.info(f"   Audience: {request.target_audience}")
        
        try:
            # Phase 1: Aggregate data
            self.logger.info("🎭 Phase transition: INIT → DATA_AGGREGATION")
            aggregated_data = self._aggregate_ast_data(request.analysis_path)
            
            # Phase 2: Select template
            self.logger.info("🎭 Phase transition: DATA_AGGREGATION → TEMPLATE_SELECTION")
            template = self._select_template(request.narrative_type, request.target_audience)
            
            # Phase 3: Generate narrative sections
            self.logger.info("🎭 Phase transition: TEMPLATE_SELECTION → NARRATIVE_SYNTHESIS")
            self.narrative_sections = self._synthesize_narrative_sections(
                aggregated_data, 
                template,
                request.max_length
            )
            
            # Phase 4: Assemble final document
            self.logger.info("🎭 Phase transition: NARRATIVE_SYNTHESIS → ASSEMBLY")
            final_narrative = self._assemble_narrative(self.narrative_sections, template)
            
            # Phase 5: Validate and save
            self.logger.info("🎭 Phase transition: ASSEMBLY → VALIDATION")
            validation_result = self._validate_narrative(final_narrative, request)
            
            if validation_result['valid']:
                self._save_narrative(final_narrative, request.output_path)
                self.logger.info("🎭 Orchestrator completing: ✅ NARRATIVE GENERATION COMPLETE")
                
                return {
                    'success': True,
                    'narrative': final_narrative,
                    'word_count': sum(s.word_count for s in self.narrative_sections),
                    'sections': len(self.narrative_sections),
                    'data_sources': list(set(sum([s.data_sources for s in self.narrative_sections], []))),
                    'output_path': str(request.output_path)
                }
            else:
                return {
                    'success': False,
                    'errors': validation_result['errors']
                }
                
        except Exception as e:
            self.logger.error(f"Narrative generation failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _aggregate_ast_data(self, analysis_path: Path) -> Dict[str, Any]:
        """
        Load and consolidate all JSON files from AST analysis.
        
        Returns:
            Dict with consolidated data from all sources
        """
        aggregated = {
            'entities': [],
            'services': [],
            'methods': [],
            'business_keywords': set(),
            'compliance_refs': [],
            'architecture_patterns': [],
            'comments': {
                'all': [],
                'regulatory': [],
                'business_rules': [],
                'tech_debt': [],
                'by_relevance': {}
            },
            'metrics': {}
        }
        
        json_files = list(analysis_path.glob('*.json'))
        self.logger.info(f"   Found {len(json_files)} JSON files to aggregate")
        
        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                # Route data to appropriate category
                if 'entities' in json_file.name.lower():
                    aggregated['entities'].extend(data if isinstance(data, list) else [data])
                elif 'service' in json_file.name.lower():
                    aggregated['services'].extend(data if isinstance(data, list) else [data])
                elif 'method' in json_file.name.lower():
                    aggregated['methods'].extend(data if isinstance(data, list) else [data])
                elif 'business' in json_file.name.lower():
                    if isinstance(data, dict) and 'keywords' in data:
                        aggregated['business_keywords'].update(data['keywords'])
                        
            except Exception as e:
                self.logger.warning(f"   Failed to load {json_file.name}: {e}")
        
        # Phase 1b: Aggregate comment data
        self.logger.info("🎭 Phase 1b: Aggregating developer comments")
        comment_data = self._aggregate_comment_data(analysis_path)
        if comment_data:
            aggregated['comments'] = comment_data
            self.logger.info(f"   Comments: {comment_data['metrics']['total']} extracted")
            self.logger.info(f"   Regulatory: {comment_data['metrics']['regulatory']}")
            self.logger.info(f"   Business Rules: {comment_data['metrics']['business']}")
            self.logger.info(f"   Tech Debt: {comment_data['metrics']['tech_debt']}")
                
        # Convert sets to lists for JSON serialization
        aggregated['business_keywords'] = list(aggregated['business_keywords'])
        
        # Calculate summary metrics
        aggregated['metrics'] = {
            'total_entities': len(aggregated['entities']),
            'total_services': len(aggregated['services']),
            'total_methods': len(aggregated['methods']),
            'total_keywords': len(aggregated['business_keywords']),
            'total_comments': len(aggregated['comments']['all']),
            'regulatory_comments': len(aggregated['comments']['regulatory']),
            'business_comments': len(aggregated['comments']['business_rules'])
        }
        
        self.logger.info(f"   Aggregated: {aggregated['metrics']}")
        return aggregated
    
    def _aggregate_comment_data(self, analysis_path: Path) -> Optional[Dict[str, Any]]:
        """
        Load comment extraction data and categorize for narrative synthesis.
        
        Returns:
            Dict with categorized comments or None if file doesn't exist
        """
        comment_file = analysis_path / 'comment-extraction.json'
        
        if not comment_file.exists():
            self.logger.info("   No comment-extraction.json found (skipping comment enhancement)")
            return None
        
        try:
            with open(comment_file, 'r', encoding='utf-8') as f:
                all_comments = json.load(f)
            
            categorized = {
                'all': all_comments,
                'regulatory': [],
                'business_rules': [],
                'tech_debt': [],
                'by_relevance': {
                    'critical': [],
                    'high': [],
                    'medium': [],
                    'low': []
                },
                'metrics': {
                    'total': len(all_comments),
                    'regulatory': 0,
                    'business': 0,
                    'tech_debt': 0
                }
            }
            
            # Categorize comments
            for comment in all_comments:
                relevance = comment.get('business_relevance', 'low')
                categorized['by_relevance'][relevance].append(comment)
                
                # Regulatory comments
                if comment.get('regulatory_keywords'):
                    categorized['regulatory'].append(comment)
                    categorized['metrics']['regulatory'] += 1
                
                # Business rule comments
                if comment.get('business_keywords'):
                    categorized['business_rules'].append(comment)
                    categorized['metrics']['business'] += 1
                
                # Technical debt markers
                if comment.get('tech_debt_marker'):
                    categorized['tech_debt'].append(comment)
                    categorized['metrics']['tech_debt'] += 1
            
            return categorized
            
        except Exception as e:
            self.logger.warning(f"   Failed to load comment data: {e}")
            return None
    
    def _select_template(self, narrative_type: str, target_audience: str) -> Dict[str, Any]:
        """
        Select appropriate narrative template based on type and audience.
        
        Returns:
            Template configuration dict
        """
        templates = {
            'executive': {
                'sections': [
                    'what_is_application',
                    'who_uses_it',
                    'key_capabilities',
                    'core_workflows',
                    'regulatory_compliance',
                    'technical_overview',
                    'integration_ecosystem'
                ],
                'tone': 'business-focused',
                'technical_depth': 'low',
                'max_jargon': False
            },
            'technical': {
                'sections': [
                    'architecture_overview',
                    'domain_model',
                    'services_layer',
                    'integration_patterns',
                    'data_access',
                    'background_jobs',
                    'code_quality'
                ],
                'tone': 'technical',
                'technical_depth': 'high',
                'max_jargon': True
            },
            'business_use_cases': {
                'sections': [
                    'primary_use_cases',
                    'user_workflows',
                    'business_rules',
                    'decision_points',
                    'success_criteria'
                ],
                'tone': 'balanced',
                'technical_depth': 'medium',
                'max_jargon': False
            },
            'compliance': {
                'sections': [
                    'regulatory_framework',
                    'irs_requirements',
                    'hipaa_security',
                    'pci_dss_scope',
                    'erisa_disclosure',
                    'audit_trail',
                    'compliance_gaps'
                ],
                'tone': 'formal',
                'technical_depth': 'medium',
                'max_jargon': False
            }
        }
        
        template = templates.get(narrative_type, templates['executive'])
        template['audience'] = target_audience
        
        self.logger.info(f"   Selected template: {narrative_type} ({len(template['sections'])} sections)")
        return template
    
    def _synthesize_narrative_sections(
        self, 
        data: Dict[str, Any], 
        template: Dict[str, Any],
        max_length: str
    ) -> List[NarrativeSection]:
        """
        Generate narrative content for each template section.
        
        This is where Copilot synthesis or LLM integration happens.
        For now, creates structured prompts for manual synthesis.
        """
        sections = []
        word_limits = {
            'brief': 75,      # Per section for 500 word total
            'standard': 200,   # Per section for 1500 word total
            'detailed': 400    # Per section for 3000 word total
        }
        
        limit = word_limits.get(max_length, 200)
        
        for section_name in template['sections']:
            # Create synthesis prompt (for manual Copilot use or future LLM integration)
            prompt = self._create_synthesis_prompt(section_name, data, template, limit)
            
            # Placeholder for actual synthesis
            # TODO: Integrate Copilot API or local LLM here
            content = f"[SYNTHESIS PROMPT FOR: {section_name}]\n\n{prompt}\n\n[Manual synthesis required]"
            
            section = NarrativeSection(
                title=section_name.replace('_', ' ').title(),
                content=content,
                section_type=template.get('tone', 'business-focused'),
                word_count=limit,  # Estimated
                data_sources=self._identify_data_sources(section_name, data)
            )
            
            sections.append(section)
            
        self.logger.info(f"   Generated {len(sections)} narrative sections")
        return sections
    
    def _create_synthesis_prompt(
        self, 
        section_name: str, 
        data: Dict[str, Any],
        template: Dict[str, Any],
        word_limit: int
    ) -> str:
        """
        Create a structured prompt for narrative synthesis.
        This prompt can be used with Copilot or an LLM.
        """
        prompt = f"""Generate a {word_limit}-word narrative for: {section_name}

AUDIENCE: {template.get('audience', 'general')}
TONE: {template.get('tone', 'business-focused')}
TECHNICAL DEPTH: {template.get('technical_depth', 'low')}

DATA AVAILABLE:
- Entities: {data['metrics']['total_entities']} domain models
- Services: {data['metrics']['total_services']} business services
- Methods: {data['metrics']['total_methods']} operations
- Keywords: {', '.join(list(data['business_keywords'])[:20])}

REQUIREMENTS:
- Non-technical language (unless audience is developers)
- Explain "what" and "why", not implementation details
- Include real metrics from data above
- Focus on business value and outcomes

STRUCTURE:
- Opening statement (problem/purpose)
- Key points (2-3 main ideas)
- Supporting evidence (metrics, examples)
- Outcome/impact statement
"""
        return prompt
    
    def _identify_data_sources(self, section_name: str, data: Dict[str, Any]) -> List[str]:
        """Identify which JSON files contributed to this section"""
        # Simple mapping - can be enhanced
        source_map = {
            'what_is_application': ['business-value-scan.json', 'complete-csharp-analysis.json'],
            'key_capabilities': ['business-value-scan.json', 'carryover-service-methods.json'],
            'domain_model': ['batch-3-1-entities.json', 'complete-csharp-analysis.json'],
            'regulatory_compliance': ['carryover-service-methods.json', 'batch-3-1-entities.json']
        }
        
        return source_map.get(section_name, ['multiple sources'])
    
    def _assemble_narrative(self, sections: List[NarrativeSection], template: Dict[str, Any]) -> str:
        """Combine narrative sections into final document"""
        narrative_parts = [
            f"# Executive Narrative: Understanding the Reimbursement Accounts Platform",
            f"\n**Generated:** {datetime.now().strftime('%B %d, %Y')}",
            f"**Audience:** {template.get('audience', 'General').title()}",
            f"**Analysis Scope:** Complete AST-based reverse engineering\n",
            "---\n"
        ]
        
        for section in sections:
            narrative_parts.append(f"\n## {section.title}\n")
            narrative_parts.append(section.content)
            narrative_parts.append(f"\n*Data sources: {', '.join(section.data_sources)}*\n")
            
        return '\n'.join(narrative_parts)
    
    def _validate_narrative(self, narrative: str, request: NarrativeRequest) -> Dict[str, Any]:
        """Validate narrative quality and completeness"""
        errors = []
        
        # Check minimum length
        word_count = len(narrative.split())
        if word_count < 200:
            errors.append(f"Narrative too short: {word_count} words (minimum 200)")
            
        # Check for placeholder content
        if '[SYNTHESIS PROMPT' in narrative or '[Manual synthesis required]' in narrative:
            errors.append("Contains synthesis placeholders - manual content generation needed")
            
        # Check for required sections
        if request.narrative_type == 'executive':
            required_headers = ['What Is Application', 'Key Capabilities', 'Regulatory Compliance']
            for header in required_headers:
                if header not in narrative:
                    errors.append(f"Missing required section: {header}")
                    
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'word_count': word_count
        }
    
    def _save_narrative(self, narrative: str, output_path: Path):
        """Save narrative to markdown file"""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(narrative)
            
        self.logger.info(f"   Saved narrative: {output_path}")


def generate_executive_narrative(analysis_path: str, output_path: str) -> Dict[str, Any]:
    """
    Convenience function for generating executive narratives.
    
    Args:
        analysis_path: Path to RA-Domain/analysis-results/
        output_path: Where to save the narrative markdown
        
    Returns:
        Result dict with success status and metadata
    """
    orchestrator = ASTNarrativeOrchestrator()
    
    request = NarrativeRequest(
        analysis_path=Path(analysis_path),
        output_path=Path(output_path),
        narrative_type='executive',
        target_audience='leadership',
        max_length='standard'  # ~1500 words
    )
    
    return orchestrator.generate_narrative(request)


if __name__ == '__main__':
    # Example usage
    logging.basicConfig(level=logging.INFO)
    
    result = generate_executive_narrative(
        analysis_path='cortex-brain/admin/RA-Domain/analysis-results',
        output_path='cortex-brain/admin/RA-Domain/documents/executive-narrative-what-this-application-does.md'
    )
    
    print(f"\nNarrative Generation Result:")
    print(f"Success: {result['success']}")
    if result['success']:
        print(f"Word Count: {result['word_count']}")
        print(f"Sections: {result['sections']}")
        print(f"Output: {result['output_path']}")
    else:
        print(f"Errors: {result.get('errors', result.get('error'))}")
