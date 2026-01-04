#!/usr/bin/env python3
"""
🎯 CORTEX Value Scoring Engine
================================

Intelligent content quality assessment and diagram recommendation system.
Determines optimal D3.js or Mermaid diagram types based on content characteristics.

**Author:** Asif Hussain
**Version:** 1.0.0
**Date:** January 4, 2026
**Copyright:** © 2026 Asif Hussain. All rights reserved.
"""

import re
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
from enum import Enum


class DiagramType(Enum):
    """Supported diagram types with complexity ratings."""
    
    # D3.js diagrams (preferred for rich interactivity)
    D3_FORCE_DIRECTED = ("d3-force-directed", 10, "Network relationships, architecture")
    D3_TREE = ("d3-tree", 8, "Hierarchical structures, taxonomy")
    D3_SUNBURST = ("d3-sunburst", 9, "Nested hierarchies, file systems")
    D3_SANKEY = ("d3-sankey", 9, "Flow analysis, data pipelines")
    D3_TIMELINE = ("d3-timeline", 7, "Sequential events, history")
    D3_BUBBLE_CHART = ("d3-bubble", 6, "Categorized metrics, comparisons")
    D3_CHORD = ("d3-chord", 10, "Complex relationships, dependencies")
    D3_TREEMAP = ("d3-treemap", 7, "Part-to-whole, resource allocation")
    
    # Mermaid diagrams (fallback for simpler visualizations)
    MERMAID_FLOWCHART = ("mermaid-flowchart", 5, "Process flows, decision trees")
    MERMAID_SEQUENCE = ("mermaid-sequence", 6, "Interaction flows, API calls")
    MERMAID_CLASS = ("mermaid-class", 7, "Object models, inheritance")
    MERMAID_STATE = ("mermaid-state", 6, "State machines, lifecycles")
    MERMAID_GANTT = ("mermaid-gantt", 5, "Project timelines, schedules")
    MERMAID_PIE = ("mermaid-pie", 3, "Simple distributions")
    MERMAID_MINDMAP = ("mermaid-mindmap", 8, "Concept relationships, brainstorming")
    MERMAID_GITGRAPH = ("mermaid-gitgraph", 6, "Version control flows")
    
    def __init__(self, diagram_id: str, complexity: int, use_case: str):
        self.diagram_id = diagram_id
        self.complexity = complexity
        self.use_case = use_case


@dataclass
class ContentMetrics:
    """Content quality and complexity metrics."""
    
    # Text analysis
    word_count: int = 0
    sentence_count: int = 0
    paragraph_count: int = 0
    avg_sentence_length: float = 0.0
    
    # Structure analysis
    heading_count: int = 0
    list_count: int = 0
    code_block_count: int = 0
    link_count: int = 0
    
    # Technical depth
    technical_terms: int = 0
    code_snippets: int = 0
    api_references: int = 0
    
    # Relationship indicators
    process_indicators: int = 0  # "then", "next", "after", "before"
    hierarchy_indicators: int = 0  # "parent", "child", "tier", "level"
    relationship_indicators: int = 0  # "connects", "depends", "requires"
    sequence_indicators: int = 0  # "first", "second", "step"
    comparison_indicators: int = 0  # "vs", "versus", "compared to"
    
    # Semantic categories
    architectural_concepts: int = 0
    workflow_concepts: int = 0
    data_flow_concepts: int = 0
    temporal_concepts: int = 0
    categorical_concepts: int = 0


@dataclass
class ValueScore:
    """Content value assessment with scoring breakdown."""
    
    total_score: int = 0
    educational_value: int = 0  # 0-30 points
    technical_depth: int = 0    # 0-30 points
    structural_quality: int = 0 # 0-20 points
    visualization_need: int = 0 # 0-20 points
    
    recommended_diagrams: List[Tuple[DiagramType, int, str]] = field(default_factory=list)
    quality_tier: str = "LOW"  # LOW, MEDIUM, HIGH, EXCEPTIONAL
    
    def calculate_tier(self):
        """Determine quality tier based on total score."""
        if self.total_score >= 85:
            self.quality_tier = "EXCEPTIONAL"
        elif self.total_score >= 70:
            self.quality_tier = "HIGH"
        elif self.total_score >= 50:
            self.quality_tier = "MEDIUM"
        else:
            self.quality_tier = "LOW"


class ValueScoringEngine:
    """Intelligent content analysis and diagram recommendation engine."""
    
    def __init__(self):
        self.technical_terms = {
            'api', 'algorithm', 'architecture', 'async', 'authentication',
            'cache', 'class', 'component', 'database', 'dependency',
            'endpoint', 'framework', 'function', 'interface', 'library',
            'method', 'module', 'object', 'orchestrator', 'pattern',
            'pipeline', 'protocol', 'query', 'repository', 'schema',
            'service', 'system', 'template', 'tier', 'token', 'workflow'
        }
        
        self.process_keywords = {
            'then', 'next', 'after', 'before', 'finally', 'subsequently',
            'execute', 'process', 'perform', 'invoke', 'trigger', 'flow'
        }
        
        self.hierarchy_keywords = {
            'parent', 'child', 'tier', 'level', 'layer', 'structure',
            'hierarchy', 'tree', 'nested', 'sub', 'branch', 'root'
        }
        
        self.relationship_keywords = {
            'connects', 'depends', 'requires', 'uses', 'implements',
            'extends', 'inherits', 'references', 'links', 'relates'
        }
        
        self.sequence_keywords = {
            'first', 'second', 'third', 'step', 'phase', 'stage',
            'begin', 'start', 'end', 'finish', 'complete', 'sequence'
        }
    
    def analyze_content(self, content: str) -> ContentMetrics:
        """Extract comprehensive metrics from content."""
        metrics = ContentMetrics()
        
        # Basic text metrics
        words = content.split()
        metrics.word_count = len(words)
        
        sentences = re.split(r'[.!?]+', content)
        metrics.sentence_count = len([s for s in sentences if s.strip()])
        
        paragraphs = content.split('\n\n')
        metrics.paragraph_count = len([p for p in paragraphs if p.strip()])
        
        if metrics.sentence_count > 0:
            metrics.avg_sentence_length = metrics.word_count / metrics.sentence_count
        
        # Structure metrics
        metrics.heading_count = len(re.findall(r'^#{1,6}\s+', content, re.MULTILINE))
        metrics.list_count = len(re.findall(r'^[-*+]\s+', content, re.MULTILINE))
        metrics.code_block_count = len(re.findall(r'```[\s\S]*?```', content))
        metrics.link_count = len(re.findall(r'\[([^\]]+)\]\(([^\)]+)\)', content))
        
        # Technical depth
        content_lower = content.lower()
        for term in self.technical_terms:
            metrics.technical_terms += len(re.findall(r'\b' + term + r'\b', content_lower))
        
        metrics.code_snippets = content.count('`')
        metrics.api_references = len(re.findall(r'\bAPI\b|\bapi\b|endpoint|request|response', content))
        
        # Relationship indicators
        for keyword in self.process_keywords:
            metrics.process_indicators += len(re.findall(r'\b' + keyword + r'\b', content_lower))
        
        for keyword in self.hierarchy_keywords:
            metrics.hierarchy_indicators += len(re.findall(r'\b' + keyword + r'\b', content_lower))
        
        for keyword in self.relationship_keywords:
            metrics.relationship_indicators += len(re.findall(r'\b' + keyword + r'\b', content_lower))
        
        for keyword in self.sequence_keywords:
            metrics.sequence_indicators += len(re.findall(r'\b' + keyword + r'\b', content_lower))
        
        metrics.comparison_indicators = len(re.findall(r'\bvs\b|\bversus\b|compared to', content_lower))
        
        # Semantic categories
        metrics.architectural_concepts = len(re.findall(
            r'\barchitecture\b|\bcomponent\b|\bmodule\b|\bsystem\b|\btier\b', content_lower
        ))
        metrics.workflow_concepts = len(re.findall(
            r'\bworkflow\b|\bpipeline\b|\bprocess\b|\bexecution\b|\borchestrat', content_lower
        ))
        metrics.data_flow_concepts = len(re.findall(
            r'\bdata flow\b|\binput\b|\boutput\b|\btransform\b|\bpipeline\b', content_lower
        ))
        metrics.temporal_concepts = len(re.findall(
            r'\btime\b|\bduration\b|\bschedule\b|\bsequence\b|\bhistory\b', content_lower
        ))
        metrics.categorical_concepts = len(re.findall(
            r'\bcategory\b|\btype\b|\bkind\b|\bclass\b|\bgroup\b', content_lower
        ))
        
        return metrics
    
    def calculate_value_score(self, metrics: ContentMetrics) -> ValueScore:
        """Calculate comprehensive value score with breakdown."""
        score = ValueScore()
        
        # Educational Value (0-30 points)
        if metrics.word_count >= 500:
            score.educational_value += 10
        elif metrics.word_count >= 200:
            score.educational_value += 5
        
        if metrics.heading_count >= 3:
            score.educational_value += 5
        
        if metrics.code_block_count >= 2:
            score.educational_value += 8
        
        if metrics.list_count >= 3:
            score.educational_value += 5
        
        if metrics.link_count >= 5:
            score.educational_value += 2
        
        # Technical Depth (0-30 points)
        tech_density = metrics.technical_terms / max(metrics.word_count, 1) * 100
        if tech_density >= 5:
            score.technical_depth += 15
        elif tech_density >= 3:
            score.technical_depth += 10
        elif tech_density >= 1:
            score.technical_depth += 5
        
        if metrics.api_references >= 3:
            score.technical_depth += 10
        
        if metrics.code_snippets >= 10:
            score.technical_depth += 5
        
        # Structural Quality (0-20 points)
        if 15 <= metrics.avg_sentence_length <= 25:
            score.structural_quality += 5  # Optimal readability
        
        if 3 <= metrics.paragraph_count <= 10:
            score.structural_quality += 5  # Well-structured
        
        if metrics.heading_count >= 4:
            score.structural_quality += 5  # Good organization
        
        if metrics.list_count >= 2:
            score.structural_quality += 5  # Clear formatting
        
        # Visualization Need (0-20 points)
        total_indicators = (
            metrics.process_indicators +
            metrics.hierarchy_indicators +
            metrics.relationship_indicators +
            metrics.sequence_indicators
        )
        
        if total_indicators >= 15:
            score.visualization_need += 20
        elif total_indicators >= 10:
            score.visualization_need += 15
        elif total_indicators >= 5:
            score.visualization_need += 10
        
        # Calculate total
        score.total_score = (
            score.educational_value +
            score.technical_depth +
            score.structural_quality +
            score.visualization_need
        )
        
        score.calculate_tier()
        
        return score
    
    def recommend_diagrams(
        self,
        metrics: ContentMetrics,
        max_recommendations: int = 3
    ) -> List[Tuple[DiagramType, int, str]]:
        """Recommend optimal diagram types based on content analysis."""
        recommendations = []
        
        # Architecture/hierarchy → Force-directed or Tree
        if metrics.architectural_concepts >= 5 or metrics.hierarchy_indicators >= 8:
            if metrics.relationship_indicators >= 5:
                recommendations.append((
                    DiagramType.D3_FORCE_DIRECTED,
                    95,
                    "Complex architectural relationships detected"
                ))
            else:
                recommendations.append((
                    DiagramType.D3_TREE,
                    90,
                    "Clear hierarchical structure detected"
                ))
        
        # Workflow/process → Sankey or Flowchart
        if metrics.workflow_concepts >= 5 or metrics.process_indicators >= 10:
            if metrics.data_flow_concepts >= 5:
                recommendations.append((
                    DiagramType.D3_SANKEY,
                    92,
                    "Data flow patterns detected"
                ))
            else:
                recommendations.append((
                    DiagramType.MERMAID_FLOWCHART,
                    85,
                    "Process flow detected"
                ))
        
        # Sequence/temporal → Timeline or Sequence
        if metrics.sequence_indicators >= 8 or metrics.temporal_concepts >= 5:
            if metrics.api_references >= 3:
                recommendations.append((
                    DiagramType.MERMAID_SEQUENCE,
                    88,
                    "API interaction sequence detected"
                ))
            else:
                recommendations.append((
                    DiagramType.D3_TIMELINE,
                    85,
                    "Temporal sequence detected"
                ))
        
        # Relationships/connections → Chord or Mindmap
        if metrics.relationship_indicators >= 10:
            recommendations.append((
                DiagramType.D3_CHORD,
                90,
                "Complex interconnections detected"
            ))
        elif metrics.relationship_indicators >= 5:
            recommendations.append((
                DiagramType.MERMAID_MINDMAP,
                82,
                "Concept relationships detected"
            ))
        
        # Categorization → Treemap or Sunburst
        if metrics.categorical_concepts >= 8:
            if metrics.hierarchy_indicators >= 5:
                recommendations.append((
                    DiagramType.D3_SUNBURST,
                    88,
                    "Nested categories detected"
                ))
            else:
                recommendations.append((
                    DiagramType.D3_TREEMAP,
                    85,
                    "Categorical distribution detected"
                ))
        
        # State transitions → State diagram
        if re.search(r'\bstate\b|\btransition\b|\blifecycle\b', metrics.__dict__.get('_raw_content', '').lower()):
            recommendations.append((
                DiagramType.MERMAID_STATE,
                87,
                "State machine detected"
            ))
        
        # Sort by confidence and return top N
        recommendations.sort(key=lambda x: x[1], reverse=True)
        return recommendations[:max_recommendations]
    
    def analyze_html_page(self, html_path: Path) -> Dict:
        """Analyze an HTML page and generate comprehensive report."""
        try:
            content = html_path.read_text(encoding='utf-8')
            
            # Extract text content (remove HTML tags)
            text_content = re.sub(r'<[^>]+>', '', content)
            text_content = re.sub(r'\s+', ' ', text_content)
            
            # Store raw content for advanced analysis
            metrics = self.analyze_content(text_content)
            metrics._raw_content = text_content  # For state machine detection
            
            score = self.calculate_value_score(metrics)
            recommendations = self.recommend_diagrams(metrics)
            
            return {
                'file_path': str(html_path),
                'metrics': {
                    'word_count': metrics.word_count,
                    'sentence_count': metrics.sentence_count,
                    'paragraph_count': metrics.paragraph_count,
                    'heading_count': metrics.heading_count,
                    'technical_terms': metrics.technical_terms,
                    'code_blocks': metrics.code_block_count,
                    'indicators': {
                        'process': metrics.process_indicators,
                        'hierarchy': metrics.hierarchy_indicators,
                        'relationship': metrics.relationship_indicators,
                        'sequence': metrics.sequence_indicators,
                    }
                },
                'value_score': {
                    'total': score.total_score,
                    'educational_value': score.educational_value,
                    'technical_depth': score.technical_depth,
                    'structural_quality': score.structural_quality,
                    'visualization_need': score.visualization_need,
                    'quality_tier': score.quality_tier
                },
                'diagram_recommendations': [
                    {
                        'type': rec[0].diagram_id,
                        'confidence': rec[1],
                        'reason': rec[2],
                        'complexity': rec[0].complexity,
                        'use_case': rec[0].use_case
                    }
                    for rec in recommendations
                ]
            }
        except Exception as e:
            return {
                'file_path': str(html_path),
                'error': str(e)
            }
    
    def batch_analyze(self, docs_dir: Path, output_file: Path):
        """Analyze all HTML files and generate comprehensive report."""
        results = []
        
        html_files = list(docs_dir.rglob('*.html'))
        print(f"🔍 Analyzing {len(html_files)} HTML files...")
        
        for html_file in html_files:
            result = self.analyze_html_page(html_file)
            results.append(result)
            
            # Print progress
            score = result.get('value_score', {})
            if 'total' in score:
                tier = score['quality_tier']
                total = score['total']
                print(f"  {'✅' if tier in ['HIGH', 'EXCEPTIONAL'] else '📊'} {html_file.name}: {total} ({tier})")
        
        # Sort by value score (descending)
        results.sort(
            key=lambda x: x.get('value_score', {}).get('total', 0),
            reverse=True
        )
        
        # Generate summary statistics
        summary = {
            'total_files': len(results),
            'tier_distribution': {
                'EXCEPTIONAL': len([r for r in results if r.get('value_score', {}).get('quality_tier') == 'EXCEPTIONAL']),
                'HIGH': len([r for r in results if r.get('value_score', {}).get('quality_tier') == 'HIGH']),
                'MEDIUM': len([r for r in results if r.get('value_score', {}).get('quality_tier') == 'MEDIUM']),
                'LOW': len([r for r in results if r.get('value_score', {}).get('quality_tier') == 'LOW']),
            },
            'avg_score': sum(r.get('value_score', {}).get('total', 0) for r in results) / len(results),
            'top_10_pages': [
                {
                    'file': r['file_path'],
                    'score': r['value_score']['total'],
                    'tier': r['value_score']['quality_tier']
                }
                for r in results[:10]
            ]
        }
        
        # Write results
        output = {
            'summary': summary,
            'detailed_results': results
        }
        
        output_file.write_text(json.dumps(output, indent=2), encoding='utf-8')
        print(f"\n✅ Analysis complete: {output_file}")
        print(f"📊 Summary: {summary['tier_distribution']}")


if __name__ == '__main__':
    engine = ValueScoringEngine()
    docs_dir = Path(__file__).parent.parent / 'docs'
    output_file = Path(__file__).parent.parent / 'reports' / 'value-scoring-analysis.json'
    
    output_file.parent.mkdir(parents=True, exist_ok=True)
    engine.batch_analyze(docs_dir, output_file)
