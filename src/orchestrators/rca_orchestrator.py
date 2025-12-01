"""
RCA (Root Cause Analysis) Orchestrator - CORTEX 3.4.0

Purpose: Interactive Root Cause Analysis with 5 Whys methodology and executive reporting
Architecture: Document processing + Interactive questioning + Knowledge graph learning + Report generation

Features:
- DOCX to Markdown conversion for existing RCA documents
- Interactive 5 Whys methodology with guided questioning
- Causal chain tracking with confidence scoring
- Pattern learning for future analyses
- Executive-ready reports for senior leadership
- Integration with InvestigationRouter for deep analysis

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json
import re


class RCAStatus(Enum):
    """RCA analysis status states"""
    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    COMPLETED = "completed"


class WhyDepth(Enum):
    """Depth levels for 5 Whys analysis"""
    WHY_1 = 1
    WHY_2 = 2
    WHY_3 = 3
    WHY_4 = 4
    WHY_5 = 5


@dataclass
class IncidentDetails:
    """Structured incident information"""
    incident_id: str
    title: str
    description: str
    occurred_at: datetime
    detected_at: datetime
    resolved_at: Optional[datetime] = None
    severity: str = "medium"  # low, medium, high, critical
    impact: str = ""
    affected_systems: List[str] = field(default_factory=list)
    affected_users: str = ""
    business_impact: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WhyQuestion:
    """A single Why question in the 5 Whys chain"""
    depth: WhyDepth
    question: str
    answer: str = ""
    confidence: float = 0.0
    evidence: List[str] = field(default_factory=list)
    follow_up_suggestions: List[str] = field(default_factory=list)
    verified: bool = False
    asked_at: Optional[datetime] = None
    answered_at: Optional[datetime] = None


@dataclass
class RootCause:
    """Identified root cause with supporting evidence"""
    description: str
    confidence: float
    evidence: List[str]
    contributing_factors: List[str] = field(default_factory=list)
    why_chain: List[WhyQuestion] = field(default_factory=list)
    category: str = "technical"  # technical, process, human, organizational
    verified: bool = False


@dataclass
class CorrectiveAction:
    """Action to address the root cause"""
    action_id: str
    description: str
    action_type: str  # immediate, short_term, long_term
    owner: str = ""
    due_date: Optional[datetime] = None
    status: str = "pending"
    impact: str = ""
    effort: str = ""  # low, medium, high
    priority: str = "medium"  # low, medium, high, critical


@dataclass
class RCAAnalysis:
    """Complete RCA analysis structure"""
    analysis_id: str
    incident: IncidentDetails
    status: RCAStatus
    
    # Timeline
    timeline: List[Dict[str, Any]] = field(default_factory=list)
    
    # 5 Whys Analysis
    why_questions: List[WhyQuestion] = field(default_factory=list)
    current_depth: int = 0
    
    # Root Cause
    root_causes: List[RootCause] = field(default_factory=list)
    
    # Actions
    corrective_actions: List[CorrectiveAction] = field(default_factory=list)
    preventive_actions: List[CorrectiveAction] = field(default_factory=list)
    
    # Metadata
    analyst: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    reviewed_by: str = ""
    approved_by: str = ""
    
    # Storage paths
    source_file: Optional[Path] = None
    analysis_file: Optional[Path] = None
    report_file: Optional[Path] = None


class RCAOrchestrator:
    """
    Orchestrates Root Cause Analysis workflows with 5 Whys methodology
    
    Key Features:
    - Document processing (DOCX → Markdown)
    - Interactive 5 Whys questioning
    - Causal chain analysis
    - Pattern learning from historical RCAs
    - Executive report generation
    """
    
    def __init__(self, brain_path: Path):
        self.logger = logging.getLogger(__name__)
        self.brain_path = brain_path
        self.rca_base_path = brain_path / "documents" / "investigations" / "rca"
        self.rca_base_path.mkdir(parents=True, exist_ok=True)
        
        # RCA subdirectories
        self.active_path = self.rca_base_path / "active"
        self.completed_path = self.rca_base_path / "completed"
        self.approved_path = self.rca_base_path / "approved"
        self.templates_path = self.rca_base_path / "templates"
        
        for path in [self.active_path, self.completed_path, self.approved_path, self.templates_path]:
            path.mkdir(exist_ok=True)
        
        # Initialize knowledge graph for pattern learning
        try:
            from src.tier2.knowledge_graph import KnowledgeGraph
            self.knowledge_graph = KnowledgeGraph()
        except ImportError:
            self.logger.warning("Knowledge graph not available, pattern learning disabled")
            self.knowledge_graph = None
        
        # Load historical patterns
        self.historical_patterns = self._load_historical_patterns()
    
    def import_rca_document(self, docx_path: Path, incident_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Import existing RCA document (DOCX format) and convert to CORTEX format
        
        Args:
            docx_path: Path to DOCX file
            incident_id: Optional incident ID (auto-generated if not provided)
            
        Returns:
            Import result with analysis_id and file paths
        """
        self.logger.info(f"Importing RCA document: {docx_path}")
        
        if not docx_path.exists():
            return {
                "success": False,
                "error": f"File not found: {docx_path}"
            }
        
        try:
            # Convert DOCX to Markdown
            markdown_content = self._convert_docx_to_markdown(docx_path)
            
            # Extract incident details from document
            incident_details = self._extract_incident_details(markdown_content)
            
            # Generate analysis ID
            analysis_id = incident_id or self._generate_analysis_id(incident_details)
            
            # Create RCA analysis structure
            analysis = RCAAnalysis(
                analysis_id=analysis_id,
                incident=incident_details,
                status=RCAStatus.DRAFT,
                source_file=docx_path
            )
            
            # Save to active directory
            analysis_file = self.active_path / f"RCA-{analysis_id}.md"
            self._save_analysis(analysis, analysis_file, markdown_content)
            analysis.analysis_file = analysis_file
            
            self.logger.info(f"RCA document imported successfully: {analysis_id}")
            
            return {
                "success": True,
                "analysis_id": analysis_id,
                "analysis_file": str(analysis_file),
                "status": "Document imported, ready for 5 Whys analysis",
                "next_steps": [
                    f"Start 5 Whys analysis: `analyze rca {analysis_id}`",
                    f"View document: `show rca {analysis_id}`",
                    "Continue with interactive questioning to identify root cause"
                ]
            }
            
        except Exception as e:
            self.logger.error(f"Error importing RCA document: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }
    
    def start_5_whys_analysis(self, analysis_id: str, initial_problem: Optional[str] = None) -> Dict[str, Any]:
        """
        Start interactive 5 Whys analysis for an incident
        
        Args:
            analysis_id: Analysis ID (or incident ID)
            initial_problem: Optional problem statement (extracted from document if not provided)
            
        Returns:
            First Why question with context
        """
        self.logger.info(f"Starting 5 Whys analysis for: {analysis_id}")
        
        # Load existing analysis or create new
        analysis = self._load_analysis(analysis_id)
        
        if not analysis:
            return {
                "success": False,
                "error": f"Analysis not found: {analysis_id}",
                "suggestion": f"Import RCA document first: `import rca [file_path]`"
            }
        
        # Update status
        analysis.status = RCAStatus.IN_PROGRESS
        analysis.updated_at = datetime.now()
        
        # Determine initial problem statement
        if not initial_problem:
            initial_problem = analysis.incident.description or "Unknown incident"
        
        # Create first Why question
        why_1 = WhyQuestion(
            depth=WhyDepth.WHY_1,
            question=f"Why did '{initial_problem}' occur?",
            asked_at=datetime.now()
        )
        
        # Add intelligent suggestions based on incident type and historical patterns
        suggestions = self._generate_why_suggestions(
            initial_problem, 
            analysis.incident, 
            depth=1
        )
        why_1.follow_up_suggestions = suggestions
        
        analysis.why_questions.append(why_1)
        analysis.current_depth = 1
        
        # Save analysis
        self._save_analysis_state(analysis)
        
        return {
            "success": True,
            "analysis_id": analysis_id,
            "current_depth": 1,
            "question": why_1.question,
            "suggestions": suggestions,
            "context": {
                "incident_title": analysis.incident.title,
                "severity": analysis.incident.severity,
                "affected_systems": analysis.incident.affected_systems
            },
            "instruction": "Answer with observed facts and evidence. I'll guide you through 5 levels of 'Why' to find the root cause."
        }
    
    def answer_why_question(self, analysis_id: str, answer: str, evidence: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Record answer to current Why question and generate next question
        
        Args:
            analysis_id: Analysis ID
            answer: User's answer to current Why question
            evidence: Optional supporting evidence
            
        Returns:
            Next Why question or root cause summary if complete
        """
        self.logger.info(f"Recording answer for {analysis_id}, depth: {answer[:50]}...")
        
        analysis = self._load_analysis(analysis_id)
        
        if not analysis:
            return {"success": False, "error": f"Analysis not found: {analysis_id}"}
        
        if not analysis.why_questions:
            return {
                "success": False,
                "error": "No active Why questions. Start analysis first: `analyze rca [id]`"
            }
        
        # Get current question
        current_question = analysis.why_questions[-1]
        
        if current_question.answer:
            return {
                "success": False,
                "error": "Current question already answered. Use `continue rca [id]` to proceed to next question."
            }
        
        # Record answer
        current_question.answer = answer
        current_question.answered_at = datetime.now()
        if evidence:
            current_question.evidence.extend(evidence)
        
        # Assess answer confidence using pattern matching
        confidence = self._assess_answer_confidence(answer, current_question, analysis)
        current_question.confidence = confidence
        
        # Check if we've reached sufficient depth
        current_depth = current_question.depth.value
        
        if current_depth >= 5:
            # Complete analysis, identify root cause
            return self._complete_5_whys_analysis(analysis)
        
        # Check if we've found true root cause early (high confidence pattern match)
        if confidence > 0.90 and current_depth >= 3:
            return {
                "success": True,
                "analysis_id": analysis_id,
                "message": f"High confidence root cause identified at Why {current_depth}",
                "root_cause_candidate": answer,
                "confidence": confidence,
                "options": [
                    f"Accept as root cause: `accept root cause {analysis_id}`",
                    f"Continue to Why {current_depth + 1}: `continue rca {analysis_id}`"
                ]
            }
        
        # Generate next Why question
        next_depth = current_depth + 1
        next_why = WhyQuestion(
            depth=WhyDepth(next_depth),
            question=f"Why {answer}?",
            asked_at=datetime.now()
        )
        
        # Generate suggestions for next level
        suggestions = self._generate_why_suggestions(
            answer,
            analysis.incident,
            depth=next_depth,
            previous_answers=[q.answer for q in analysis.why_questions if q.answer]
        )
        next_why.follow_up_suggestions = suggestions
        
        analysis.why_questions.append(next_why)
        analysis.current_depth = next_depth
        analysis.updated_at = datetime.now()
        
        # Save state
        self._save_analysis_state(analysis)
        
        return {
            "success": True,
            "analysis_id": analysis_id,
            "current_depth": next_depth,
            "question": next_why.question,
            "suggestions": suggestions,
            "previous_answer_confidence": confidence,
            "progress": f"Why {next_depth} of 5",
            "causal_chain": self._format_causal_chain(analysis.why_questions)
        }
    
    def generate_executive_report(self, analysis_id: str, include_appendix: bool = True) -> Dict[str, Any]:
        """
        Generate executive-ready RCA report for senior leadership
        
        Args:
            analysis_id: Analysis ID
            include_appendix: Include technical appendix
            
        Returns:
            Report generation result with file path
        """
        self.logger.info(f"Generating executive report for: {analysis_id}")
        
        analysis = self._load_analysis(analysis_id)
        
        if not analysis:
            return {"success": False, "error": f"Analysis not found: {analysis_id}"}
        
        if not analysis.root_causes:
            return {
                "success": False,
                "error": "Root cause analysis not complete. Complete 5 Whys analysis first."
            }
        
        # Generate report sections
        report_sections = []
        
        # 1. Executive Summary
        exec_summary = self._generate_executive_summary(analysis)
        report_sections.append(exec_summary)
        
        # 2. Incident Overview
        incident_overview = self._generate_incident_overview(analysis)
        report_sections.append(incident_overview)
        
        # 3. Timeline
        timeline_section = self._generate_timeline_section(analysis)
        report_sections.append(timeline_section)
        
        # 4. Root Cause Analysis (5 Whys)
        root_cause_section = self._generate_root_cause_section(analysis)
        report_sections.append(root_cause_section)
        
        # 5. Impact Assessment
        impact_section = self._generate_impact_assessment(analysis)
        report_sections.append(impact_section)
        
        # 6. Corrective Actions
        corrective_section = self._generate_corrective_actions_section(analysis)
        report_sections.append(corrective_section)
        
        # 7. Prevention Strategy
        prevention_section = self._generate_prevention_strategy(analysis)
        report_sections.append(prevention_section)
        
        # 8. Recommendations
        recommendations_section = self._generate_recommendations_section(analysis)
        report_sections.append(recommendations_section)
        
        # 9. Appendix (if requested)
        if include_appendix:
            appendix = self._generate_technical_appendix(analysis)
            report_sections.append(appendix)
        
        # Compile full report
        full_report = self._compile_report(analysis, report_sections)
        
        # Save report
        report_file = self.approved_path / f"RCA-REPORT-{analysis_id}-{datetime.now().strftime('%Y%m%d')}.md"
        report_file.write_text(full_report, encoding='utf-8')
        
        analysis.report_file = report_file
        analysis.status = RCAStatus.UNDER_REVIEW
        analysis.updated_at = datetime.now()
        self._save_analysis_state(analysis)
        
        self.logger.info(f"Executive report generated: {report_file}")
        
        return {
            "success": True,
            "analysis_id": analysis_id,
            "report_file": str(report_file),
            "sections": len(report_sections),
            "status": "Report ready for review",
            "next_steps": [
                f"Review report: Open {report_file.name}",
                f"Approve RCA: `approve rca {analysis_id}`",
                "Share with senior leadership"
            ]
        }
    
    def list_active_rcas(self) -> Dict[str, Any]:
        """List all active RCA analyses"""
        active_analyses = []
        
        for file in self.active_path.glob("RCA-*.md"):
            try:
                metadata = self._extract_metadata_from_file(file)
                active_analyses.append(metadata)
            except Exception as e:
                self.logger.warning(f"Could not read {file}: {e}")
        
        return {
            "success": True,
            "count": len(active_analyses),
            "analyses": active_analyses
        }
    
    def _convert_docx_to_markdown(self, docx_path: Path) -> str:
        """Convert DOCX file to Markdown format"""
        try:
            # Try using python-docx if available
            try:
                import docx
                doc = docx.Document(str(docx_path))
                
                markdown_lines = []
                markdown_lines.append(f"# RCA Document: {docx_path.stem}\n")
                markdown_lines.append(f"**Imported:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
                markdown_lines.append(f"**Source:** {docx_path.name}\n\n")
                markdown_lines.append("---\n\n")
                
                for para in doc.paragraphs:
                    text = para.text.strip()
                    if text:
                        # Detect headings based on style or formatting
                        if para.style.name.startswith('Heading'):
                            level = int(para.style.name[-1]) if para.style.name[-1].isdigit() else 2
                            markdown_lines.append(f"{'#' * level} {text}\n\n")
                        else:
                            markdown_lines.append(f"{text}\n\n")
                
                return ''.join(markdown_lines)
                
            except ImportError:
                # Fallback: Create placeholder with instructions
                self.logger.warning("python-docx not available, creating placeholder")
                return self._create_docx_placeholder(docx_path)
                
        except Exception as e:
            self.logger.error(f"Error converting DOCX: {e}")
            return self._create_docx_placeholder(docx_path)
    
    def _create_docx_placeholder(self, docx_path: Path) -> str:
        """Create placeholder markdown for DOCX conversion"""
        return f"""# RCA Document: {docx_path.stem}

**Status:** Manual conversion required
**Source:** {docx_path.name}
**Imported:** {datetime.now().strftime('%Y-%m-%d %H:%M')}

---

## ⚠️ Conversion Required

The DOCX file could not be automatically converted. Please manually copy the content below:

### Instructions:
1. Open the DOCX file: `{docx_path}`
2. Copy the relevant sections (Incident Details, Timeline, Analysis)
3. Paste content below and save this file

---

## Incident Details

[Paste incident details here]

## Timeline

[Paste timeline here]

## Initial Analysis

[Paste initial analysis here]

---

After pasting content, save this file and run: `analyze rca {docx_path.stem}`
"""
    
    def _extract_incident_details(self, markdown_content: str) -> IncidentDetails:
        """Extract structured incident details from markdown content"""
        
        # Extract title (first H1 heading)
        title_match = re.search(r'^#\s+(.+)$', markdown_content, re.MULTILINE)
        title = title_match.group(1) if title_match else "Untitled Incident"
        
        # Extract dates
        occurred_at = datetime.now()
        detected_at = datetime.now()
        
        date_patterns = [
            r'occurred?:?\s*(\d{4}-\d{2}-\d{2})',
            r'incident date:?\s*(\d{4}-\d{2}-\d{2})',
            r'date:?\s*(\d{4}-\d{2}-\d{2})'
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, markdown_content, re.IGNORECASE)
            if match:
                try:
                    occurred_at = datetime.strptime(match.group(1), '%Y-%m-%d')
                    break
                except ValueError:
                    pass
        
        # Extract severity
        severity = "medium"
        severity_match = re.search(r'severity:?\s*(low|medium|high|critical)', markdown_content, re.IGNORECASE)
        if severity_match:
            severity = severity_match.group(1).lower()
        
        # Extract description (first paragraph after title)
        desc_match = re.search(r'^#.+?\n\n(.+?)(?:\n\n|$)', markdown_content, re.MULTILINE | re.DOTALL)
        description = desc_match.group(1).strip() if desc_match else ""
        
        # Generate incident ID
        incident_id = f"INC-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        return IncidentDetails(
            incident_id=incident_id,
            title=title,
            description=description,
            occurred_at=occurred_at,
            detected_at=detected_at,
            severity=severity
        )
    
    def _generate_analysis_id(self, incident: IncidentDetails) -> str:
        """Generate unique analysis ID"""
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        title_slug = re.sub(r'[^a-z0-9]+', '-', incident.title.lower())[:30]
        return f"{timestamp}-{title_slug}"
    
    def _save_analysis(self, analysis: RCAAnalysis, file_path: Path, original_content: str = "") -> None:
        """Save analysis to markdown file"""
        
        content_lines = []
        
        # Header
        content_lines.append(f"# RCA Analysis: {analysis.incident.title}\n")
        content_lines.append(f"**Analysis ID:** {analysis.analysis_id}\n")
        content_lines.append(f"**Status:** {analysis.status.value}\n")
        content_lines.append(f"**Created:** {analysis.created_at.strftime('%Y-%m-%d %H:%M')}\n")
        content_lines.append(f"**Updated:** {analysis.updated_at.strftime('%Y-%m-%d %H:%M')}\n\n")
        content_lines.append("---\n\n")
        
        # Incident Details
        content_lines.append("## Incident Details\n\n")
        content_lines.append(f"**Incident ID:** {analysis.incident.incident_id}\n")
        content_lines.append(f"**Severity:** {analysis.incident.severity}\n")
        content_lines.append(f"**Occurred:** {analysis.incident.occurred_at.strftime('%Y-%m-%d %H:%M')}\n")
        content_lines.append(f"**Description:** {analysis.incident.description}\n\n")
        
        # Original Content
        if original_content:
            content_lines.append("## Original Document\n\n")
            content_lines.append(original_content)
            content_lines.append("\n\n")
        
        # 5 Whys Section (if started)
        if analysis.why_questions:
            content_lines.append("## 5 Whys Analysis\n\n")
            for why_q in analysis.why_questions:
                content_lines.append(f"### Why {why_q.depth.value}\n\n")
                content_lines.append(f"**Question:** {why_q.question}\n\n")
                if why_q.answer:
                    content_lines.append(f"**Answer:** {why_q.answer}\n\n")
                    content_lines.append(f"**Confidence:** {why_q.confidence:.0%}\n\n")
                    if why_q.evidence:
                        content_lines.append("**Evidence:**\n")
                        for evidence in why_q.evidence:
                            content_lines.append(f"- {evidence}\n")
                        content_lines.append("\n")
        
        # Root Causes (if identified)
        if analysis.root_causes:
            content_lines.append("## Identified Root Causes\n\n")
            for i, root_cause in enumerate(analysis.root_causes, 1):
                content_lines.append(f"### Root Cause {i}\n\n")
                content_lines.append(f"{root_cause.description}\n\n")
                content_lines.append(f"**Confidence:** {root_cause.confidence:.0%}\n")
                content_lines.append(f"**Category:** {root_cause.category}\n\n")
        
        file_path.write_text(''.join(content_lines), encoding='utf-8')
        self.logger.info(f"Analysis saved: {file_path}")
    
    def _save_analysis_state(self, analysis: RCAAnalysis) -> None:
        """Save current analysis state"""
        if analysis.analysis_file:
            self._save_analysis(analysis, analysis.analysis_file)
    
    def _load_analysis(self, analysis_id: str) -> Optional[RCAAnalysis]:
        """Load analysis from file"""
        # Search in active directory
        file_path = self.active_path / f"RCA-{analysis_id}.md"
        
        if not file_path.exists():
            # Try finding by partial ID
            matches = list(self.active_path.glob(f"*{analysis_id}*.md"))
            if matches:
                file_path = matches[0]
            else:
                return None
        
        # Parse file and reconstruct analysis
        # For now, return None and implement full parsing later
        self.logger.warning(f"Analysis loading not fully implemented: {analysis_id}")
        return None
    
    def _generate_why_suggestions(self, current_answer: str, incident: IncidentDetails, 
                                  depth: int, previous_answers: Optional[List[str]] = None) -> List[str]:
        """Generate intelligent suggestions for Why questions using patterns"""
        
        suggestions = []
        
        # Pattern-based suggestions from knowledge graph
        if self.knowledge_graph and self.historical_patterns:
            similar_patterns = self._find_similar_patterns(current_answer, incident.affected_systems)
            suggestions.extend(similar_patterns[:3])
        
        # Generic depth-based suggestions
        depth_suggestions = {
            1: [
                "System configuration issue",
                "Code defect or bug",
                "External dependency failure",
                "Resource constraint (memory, CPU, disk)",
                "Human error or misconfiguration"
            ],
            2: [
                "Missing validation or error handling",
                "Insufficient testing coverage",
                "Lack of monitoring or alerting",
                "Incomplete requirements or specifications",
                "Technical debt or legacy code"
            ],
            3: [
                "Process gap or missing procedure",
                "Inadequate training or documentation",
                "Communication breakdown",
                "Time pressure or rushed deployment",
                "Lack of code review or peer oversight"
            ],
            4: [
                "Organizational priority misalignment",
                "Resource allocation decisions",
                "Culture of rushing vs quality",
                "Insufficient investment in tooling/automation",
                "Lack of clear ownership or accountability"
            ],
            5: [
                "Strategic direction and tradeoffs",
                "Market pressures and deadlines",
                "Organizational structure and silos",
                "Long-term technical vision gaps",
                "Risk tolerance and acceptance criteria"
            ]
        }
        
        if depth in depth_suggestions:
            suggestions.extend(depth_suggestions[depth][:3])
        
        return suggestions[:5]  # Return top 5 suggestions
    
    def _assess_answer_confidence(self, answer: str, question: WhyQuestion, 
                                  analysis: RCAAnalysis) -> float:
        """Assess confidence of answer using pattern matching and heuristics"""
        
        confidence = 0.5  # Base confidence
        
        # Length check (detailed answers = higher confidence)
        if len(answer.split()) > 15:
            confidence += 0.1
        
        # Evidence check
        if question.evidence:
            confidence += 0.15
        
        # Specificity check (contains specific terms, numbers, names)
        if re.search(r'\b\d+\b', answer):  # Contains numbers
            confidence += 0.05
        if re.search(r'\b[A-Z][a-z]+(?:[A-Z][a-z]+)+\b', answer):  # Contains CamelCase (class/method names)
            confidence += 0.1
        
        # Pattern matching against known root causes
        if self.knowledge_graph:
            pattern_match_score = self._match_against_patterns(answer)
            confidence += pattern_match_score * 0.2
        
        return min(confidence, 1.0)
    
    def _complete_5_whys_analysis(self, analysis: RCAAnalysis) -> Dict[str, Any]:
        """Complete 5 Whys analysis and identify root cause"""
        
        # Extract root cause from final Why answer
        final_why = analysis.why_questions[-1]
        
        root_cause = RootCause(
            description=final_why.answer,
            confidence=final_why.confidence,
            evidence=final_why.evidence,
            why_chain=analysis.why_questions.copy()
        )
        
        # Categorize root cause
        root_cause.category = self._categorize_root_cause(final_why.answer)
        
        analysis.root_causes.append(root_cause)
        analysis.status = RCAStatus.COMPLETED
        analysis.completed_at = datetime.now()
        
        self._save_analysis_state(analysis)
        
        # Learn from this analysis
        if self.knowledge_graph:
            self._learn_from_analysis(analysis)
        
        return {
            "success": True,
            "analysis_id": analysis.analysis_id,
            "status": "5 Whys analysis complete",
            "root_cause": root_cause.description,
            "confidence": root_cause.confidence,
            "category": root_cause.category,
            "causal_chain": self._format_causal_chain(analysis.why_questions),
            "next_steps": [
                f"Generate executive report: `report rca {analysis.analysis_id}`",
                f"Define corrective actions: `actions rca {analysis.analysis_id}`",
                f"Review analysis: `show rca {analysis.analysis_id}`"
            ]
        }
    
    def _format_causal_chain(self, why_questions: List[WhyQuestion]) -> List[str]:
        """Format the causal chain for display"""
        chain = []
        for why_q in why_questions:
            if why_q.answer:
                chain.append(f"Why {why_q.depth.value}: {why_q.answer} ({why_q.confidence:.0%} confidence)")
        return chain
    
    def _categorize_root_cause(self, root_cause_description: str) -> str:
        """Categorize root cause into technical/process/human/organizational"""
        
        description_lower = root_cause_description.lower()
        
        # Technical indicators
        technical_keywords = ['bug', 'code', 'system', 'server', 'database', 'api', 'configuration', 
                            'memory', 'cpu', 'disk', 'network', 'dependency', 'library']
        if any(keyword in description_lower for keyword in technical_keywords):
            return "technical"
        
        # Process indicators
        process_keywords = ['process', 'procedure', 'workflow', 'review', 'testing', 'deployment', 
                           'release', 'validation', 'approval', 'checklist']
        if any(keyword in description_lower for keyword in process_keywords):
            return "process"
        
        # Human indicators
        human_keywords = ['training', 'knowledge', 'error', 'mistake', 'communication', 
                         'misunderstanding', 'assumption', 'oversight']
        if any(keyword in description_lower for keyword in human_keywords):
            return "human"
        
        # Organizational indicators
        org_keywords = ['policy', 'culture', 'resource', 'priority', 'budget', 'strategy', 
                       'structure', 'management', 'leadership']
        if any(keyword in description_lower for keyword in org_keywords):
            return "organizational"
        
        return "technical"  # Default
    
    def _load_historical_patterns(self) -> List[Dict[str, Any]]:
        """Load historical RCA patterns for learning"""
        patterns = []
        
        # Load from completed RCAs
        for file in self.completed_path.glob("RCA-*.md"):
            try:
                # Extract patterns from completed analyses
                # Implementation placeholder
                pass
            except Exception as e:
                self.logger.warning(f"Could not load patterns from {file}: {e}")
        
        return patterns
    
    def _find_similar_patterns(self, answer: str, affected_systems: List[str]) -> List[str]:
        """Find similar patterns from historical analyses"""
        # Implementation placeholder
        return []
    
    def _match_against_patterns(self, answer: str) -> float:
        """Match answer against known patterns and return similarity score"""
        # Implementation placeholder
        return 0.0
    
    def _learn_from_analysis(self, analysis: RCAAnalysis) -> None:
        """Store analysis patterns in knowledge graph for future learning"""
        # Implementation placeholder
        pass
    
    def _extract_metadata_from_file(self, file: Path) -> Dict[str, Any]:
        """Extract metadata from RCA file"""
        content = file.read_text(encoding='utf-8')
        
        # Extract key fields
        analysis_id_match = re.search(r'\*\*Analysis ID:\*\*\s*(.+)', content)
        status_match = re.search(r'\*\*Status:\*\*\s*(.+)', content)
        title_match = re.search(r'^#\s+RCA Analysis:\s*(.+)$', content, re.MULTILINE)
        
        return {
            "file": file.name,
            "analysis_id": analysis_id_match.group(1).strip() if analysis_id_match else "unknown",
            "title": title_match.group(1).strip() if title_match else file.stem,
            "status": status_match.group(1).strip() if status_match else "unknown",
            "updated": datetime.fromtimestamp(file.stat().st_mtime).strftime('%Y-%m-%d %H:%M')
        }
    
    # Report generation methods
    def _generate_executive_summary(self, analysis: RCAAnalysis) -> str:
        """Generate executive summary section"""
        root_cause = analysis.root_causes[0] if analysis.root_causes else None
        
        summary = f"""## Executive Summary

**Incident:** {analysis.incident.title}
**Date:** {analysis.incident.occurred_at.strftime('%Y-%m-%d')}
**Severity:** {analysis.incident.severity.upper()}
**Status:** {analysis.status.value.replace('_', ' ').title()}

### Key Findings

"""
        
        if root_cause:
            summary += f"**Root Cause:** {root_cause.description}\n\n"
            summary += f"**Category:** {root_cause.category.title()}\n"
            summary += f"**Confidence Level:** {root_cause.confidence:.0%}\n\n"
        
        summary += f"""### Impact

{analysis.incident.business_impact or 'Business impact assessment pending.'}

### Actions Required

{len(analysis.corrective_actions)} corrective actions identified
{len(analysis.preventive_actions)} preventive measures recommended

"""
        
        return summary
    
    def _generate_incident_overview(self, analysis: RCAAnalysis) -> str:
        """Generate incident overview section"""
        incident = analysis.incident
        
        overview = f"""## Incident Overview

### Description

{incident.description}

### Timeline

- **Occurred:** {incident.occurred_at.strftime('%Y-%m-%d %H:%M %Z')}
- **Detected:** {incident.detected_at.strftime('%Y-%m-%d %H:%M %Z')}
"""
        
        if incident.resolved_at:
            overview += f"- **Resolved:** {incident.resolved_at.strftime('%Y-%m-%d %H:%M %Z')}\n"
        
        overview += f"""
### Affected Systems

"""
        
        if incident.affected_systems:
            for system in incident.affected_systems:
                overview += f"- {system}\n"
        else:
            overview += "- Not specified\n"
        
        overview += "\n"
        
        return overview
    
    def _generate_timeline_section(self, analysis: RCAAnalysis) -> str:
        """Generate timeline section"""
        timeline = """## Detailed Timeline

"""
        
        if analysis.timeline:
            for event in analysis.timeline:
                timeline += f"**{event.get('time')}** - {event.get('description')}\n\n"
        else:
            timeline += "_Timeline details to be added_\n\n"
        
        return timeline
    
    def _generate_root_cause_section(self, analysis: RCAAnalysis) -> str:
        """Generate root cause analysis section"""
        section = """## Root Cause Analysis

### 5 Whys Methodology

"""
        
        for why_q in analysis.why_questions:
            section += f"**Why {why_q.depth.value}:** {why_q.question}\n\n"
            section += f"**Answer:** {why_q.answer}\n\n"
            if why_q.evidence:
                section += "**Supporting Evidence:**\n"
                for evidence in why_q.evidence:
                    section += f"- {evidence}\n"
                section += "\n"
        
        section += "### Identified Root Cause\n\n"
        
        for root_cause in analysis.root_causes:
            section += f"{root_cause.description}\n\n"
            section += f"**Category:** {root_cause.category.title()}\n"
            section += f"**Confidence:** {root_cause.confidence:.0%}\n\n"
            
            if root_cause.contributing_factors:
                section += "**Contributing Factors:**\n"
                for factor in root_cause.contributing_factors:
                    section += f"- {factor}\n"
                section += "\n"
        
        return section
    
    def _generate_impact_assessment(self, analysis: RCAAnalysis) -> str:
        """Generate impact assessment section"""
        return f"""## Impact Assessment

### Business Impact

{analysis.incident.business_impact or '_To be determined_'}

### Affected Users

{analysis.incident.affected_users or '_To be determined_'}

### Financial Impact

_To be calculated_

### Reputational Impact

_To be assessed_

"""
    
    def _generate_corrective_actions_section(self, analysis: RCAAnalysis) -> str:
        """Generate corrective actions section"""
        section = """## Corrective Actions

### Immediate Actions

"""
        
        immediate_actions = [a for a in analysis.corrective_actions if a.action_type == 'immediate']
        
        if immediate_actions:
            for action in immediate_actions:
                section += f"- **{action.action_id}:** {action.description}\n"
                section += f"  - Owner: {action.owner or 'TBD'}\n"
                section += f"  - Status: {action.status}\n\n"
        else:
            section += "_No immediate actions defined_\n\n"
        
        section += "### Short-term Actions\n\n"
        
        short_term_actions = [a for a in analysis.corrective_actions if a.action_type == 'short_term']
        
        if short_term_actions:
            for action in short_term_actions:
                section += f"- **{action.action_id}:** {action.description}\n"
                section += f"  - Owner: {action.owner or 'TBD'}\n"
                section += f"  - Status: {action.status}\n\n"
        else:
            section += "_No short-term actions defined_\n\n"
        
        return section
    
    def _generate_prevention_strategy(self, analysis: RCAAnalysis) -> str:
        """Generate prevention strategy section"""
        section = """## Prevention Strategy

### Long-term Preventive Measures

"""
        
        if analysis.preventive_actions:
            for action in analysis.preventive_actions:
                section += f"- **{action.action_id}:** {action.description}\n"
                section += f"  - Impact: {action.impact}\n"
                section += f"  - Effort: {action.effort}\n\n"
        else:
            section += "_Preventive measures to be defined_\n\n"
        
        return section
    
    def _generate_recommendations_section(self, analysis: RCAAnalysis) -> str:
        """Generate recommendations section"""
        return """## Recommendations

### Process Improvements

1. _To be defined based on root cause category_

### Tool/Technology Enhancements

1. _To be defined_

### Training & Documentation

1. _To be defined_

### Monitoring & Alerting

1. _To be defined_

"""
    
    def _generate_technical_appendix(self, analysis: RCAAnalysis) -> str:
        """Generate technical appendix"""
        appendix = """## Appendix: Technical Details

### Log Excerpts

_To be added_

### System Configuration

_To be added_

### Code References

_To be added_

"""
        
        return appendix
    
    def _compile_report(self, analysis: RCAAnalysis, sections: List[str]) -> str:
        """Compile all sections into final report"""
        
        header = f"""# Root Cause Analysis Report
# {analysis.incident.title}

**Document Control**
- Report ID: RCA-REPORT-{analysis.analysis_id}
- Date: {datetime.now().strftime('%Y-%m-%d')}
- Analyst: {analysis.analyst or 'CORTEX RCA System'}
- Status: {analysis.status.value.replace('_', ' ').title()}

---

"""
        
        footer = f"""

---

**Report Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}
**Generated By:** CORTEX RCA Orchestrator v3.4.0
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.
"""
        
        return header + '\n\n'.join(sections) + footer
