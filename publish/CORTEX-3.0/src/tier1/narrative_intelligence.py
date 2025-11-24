"""
CORTEX 3.0 Narrative Intelligence Module
Advanced Fusion - Milestone 3

Enhanced story generation with contextual reasoning and development flow analysis.
Generates coherent narratives about development progress using conversation patterns.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file for terms
Repository: https://github.com/asifhussain60/CORTEX
"""

import json
import sqlite3
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
import logging
import re
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)


class StoryType(Enum):
    """Types of stories the narrative intelligence can generate"""
    DEVELOPMENT_PROGRESS = "development_progress"    # Overall project evolution
    FEATURE_JOURNEY = "feature_journey"             # Single feature development story
    PROBLEM_RESOLUTION = "problem_resolution"       # Bug fixing and debugging narrative
    LEARNING_EVOLUTION = "learning_evolution"       # How patterns and knowledge grew
    COLLABORATION = "collaboration"                 # Team interaction story
    TECHNICAL_DISCOVERY = "technical_discovery"     # New insights and discoveries


class NarrativeStyle(Enum):
    """Narrative styles for different audiences"""
    TECHNICAL = "technical"           # For developers and technical stakeholders
    EXECUTIVE = "executive"          # For management and business stakeholders
    STORYTELLING = "storytelling"    # Engaging narrative format
    CHRONOLOGICAL = "chronological" # Time-based factual sequence
    THEMATIC = "thematic"           # Organized by themes and topics


@dataclass
class StoryElement:
    """A single element or event in a development story"""
    element_id: str
    timestamp: datetime
    element_type: str  # 'conversation', 'file_change', 'pattern_learned', 'correlation'
    content: str
    confidence: float = 0.8
    related_files: List[str] = None
    context_tags: List[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.related_files is None:
            self.related_files = []
        if self.context_tags is None:
            self.context_tags = []
        if self.metadata is None:
            self.metadata = {}
        if self.element_id is None:
            self.element_id = f"story_elem_{uuid.uuid4().hex[:8]}"


@dataclass 
class DevelopmentNarrative:
    """A coherent narrative about development progress"""
    narrative_id: str
    title: str
    story_type: StoryType
    narrative_style: NarrativeStyle
    story_elements: List[StoryElement]
    generated_narrative: str
    metadata: Dict[str, Any]
    created_at: datetime
    confidence_score: float = 0.8
    
    def __post_init__(self):
        if self.narrative_id is None:
            self.narrative_id = f"narrative_{uuid.uuid4().hex[:8]}"
        if self.created_at is None:
            self.created_at = datetime.now()


class NarrativeIntelligence:
    """
    CORTEX 3.0 Narrative Intelligence Module
    
    Generates coherent stories about development progress by analyzing conversation patterns,
    file changes, and learning evolution. Provides contextual insights about project development.
    """
    
    def __init__(self, database_path: str, pattern_learning_engine=None):
        """
        Initialize the Narrative Intelligence Module.
        
        Args:
            database_path: Path to SQLite database for story storage
            pattern_learning_engine: Optional PatternLearningEngine for enhanced insights
        """
        self.database_path = database_path
        self.pattern_learning_engine = pattern_learning_engine
        self._ensure_schema()
        
    def _ensure_schema(self) -> None:
        """Ensure database schema exists for narrative intelligence"""
        try:
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()
                
                # Create story_elements table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS story_elements (
                        element_id TEXT PRIMARY KEY,
                        timestamp DATETIME NOT NULL,
                        element_type TEXT NOT NULL,
                        content TEXT NOT NULL,
                        confidence REAL DEFAULT 0.8,
                        related_files TEXT,
                        context_tags TEXT,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Create development_narratives table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS development_narratives (
                        narrative_id TEXT PRIMARY KEY,
                        title TEXT NOT NULL,
                        story_type TEXT NOT NULL,
                        narrative_style TEXT NOT NULL,
                        story_elements TEXT NOT NULL,
                        generated_narrative TEXT NOT NULL,
                        metadata TEXT,
                        confidence_score REAL DEFAULT 0.8,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Create indexes for performance
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_elements_timestamp 
                    ON story_elements(timestamp DESC)
                """)
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_elements_type 
                    ON story_elements(element_type)
                """)
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_narratives_type 
                    ON development_narratives(story_type, created_at DESC)
                """)
                
                conn.commit()
                logger.info("Narrative intelligence database schema initialized")
                
        except sqlite3.Error as e:
            logger.error(f"Failed to initialize narrative intelligence schema: {e}")
            raise
    
    def add_story_element(self, element: StoryElement) -> bool:
        """Add a story element to the narrative database"""
        try:
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT OR REPLACE INTO story_elements 
                    (element_id, timestamp, element_type, content, confidence, 
                     related_files, context_tags, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    element.element_id,
                    element.timestamp.isoformat(),
                    element.element_type,
                    element.content,
                    element.confidence,
                    json.dumps(element.related_files),
                    json.dumps(element.context_tags),
                    datetime.now().isoformat()
                ))
                
                conn.commit()
                return True
                
        except sqlite3.Error as e:
            logger.error(f"Failed to add story element: {e}")
            return False
    
    def generate_development_story(self, 
                                 time_range: Tuple[datetime, datetime],
                                 story_type: StoryType = StoryType.DEVELOPMENT_PROGRESS,
                                 narrative_style: NarrativeStyle = NarrativeStyle.TECHNICAL,
                                 focus_files: List[str] = None) -> DevelopmentNarrative:
        """
        Generate a coherent narrative about development progress.
        
        Args:
            time_range: Tuple of (start_time, end_time) for story scope
            story_type: Type of story to generate
            narrative_style: Style/audience for the narrative
            focus_files: Optional list of files to focus the story on
            
        Returns:
            DevelopmentNarrative with generated story
        """
        try:
            # Gather story elements from the specified time range
            story_elements = self._gather_story_elements(time_range, focus_files)
            
            if not story_elements:
                return self._create_empty_narrative(story_type, narrative_style, time_range)
            
            # Analyze story elements for themes and patterns
            analysis = self._analyze_story_elements(story_elements, story_type)
            
            # Generate narrative based on story type and style
            narrative_text = self._generate_narrative_text(
                story_elements, analysis, story_type, narrative_style
            )
            
            # Create narrative object
            narrative = DevelopmentNarrative(
                narrative_id=None,  # Auto-generated
                title=self._generate_story_title(analysis, story_type),
                story_type=story_type,
                narrative_style=narrative_style,
                story_elements=story_elements,
                generated_narrative=narrative_text,
                metadata=analysis,
                created_at=datetime.now(),
                confidence_score=self._calculate_narrative_confidence(story_elements, analysis)
            )
            
            # Store narrative in database
            self._store_narrative(narrative)
            
            logger.info(f"Generated {story_type.value} narrative: {narrative.title}")
            return narrative
            
        except Exception as e:
            logger.error(f"Failed to generate development story: {e}")
            raise
    
    def _gather_story_elements(self, 
                              time_range: Tuple[datetime, datetime],
                              focus_files: List[str] = None) -> List[StoryElement]:
        """Gather relevant story elements from the time range"""
        try:
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()
                
                start_time, end_time = time_range
                
                # Base query for time range
                query = """
                    SELECT element_id, timestamp, element_type, content, 
                           confidence, related_files, context_tags
                    FROM story_elements 
                    WHERE timestamp BETWEEN ? AND ?
                """
                params = [start_time.isoformat(), end_time.isoformat()]
                
                # Add file filtering if specified
                if focus_files:
                    file_conditions = " OR ".join(["related_files LIKE ?" for _ in focus_files])
                    query += f" AND ({file_conditions})"
                    params.extend([f"%{file}%" for file in focus_files])
                
                query += " ORDER BY timestamp ASC"
                
                cursor.execute(query, params)
                
                elements = []
                for row in cursor.fetchall():
                    element = StoryElement(
                        element_id=row[0],
                        timestamp=datetime.fromisoformat(row[1]),
                        element_type=row[2],
                        content=row[3],
                        confidence=row[4],
                        related_files=json.loads(row[5]) if row[5] else [],
                        context_tags=json.loads(row[6]) if row[6] else []
                    )
                    elements.append(element)
                
                return elements
                
        except sqlite3.Error as e:
            logger.error(f"Failed to gather story elements: {e}")
            return []
    
    def _analyze_story_elements(self, elements: List[StoryElement], story_type: StoryType) -> Dict[str, Any]:
        """Analyze story elements to extract themes, patterns, and insights"""
        analysis = {
            "element_count": len(elements),
            "time_span_hours": 0.0,
            "file_activity": {},
            "dominant_themes": [],
            "development_phases": [],
            "complexity_indicators": [],
            "collaboration_signals": [],
            "technical_discoveries": []
        }
        
        if not elements:
            return analysis
        
        # Calculate time span
        if len(elements) > 1:
            time_span = elements[-1].timestamp - elements[0].timestamp
            analysis["time_span_hours"] = time_span.total_seconds() / 3600
        
        # Analyze file activity
        file_mentions = {}
        for element in elements:
            for file in element.related_files:
                file_mentions[file] = file_mentions.get(file, 0) + 1
        analysis["file_activity"] = dict(sorted(file_mentions.items(), 
                                               key=lambda x: x[1], reverse=True)[:10])
        
        # Extract themes from content
        all_content = " ".join([elem.content for elem in elements])
        analysis["dominant_themes"] = self._extract_themes(all_content)
        
        # Identify development phases
        analysis["development_phases"] = self._identify_development_phases(elements)
        
        # Detect complexity indicators
        analysis["complexity_indicators"] = self._detect_complexity_indicators(elements)
        
        # Find collaboration signals
        analysis["collaboration_signals"] = self._detect_collaboration_signals(elements)
        
        # Identify technical discoveries
        analysis["technical_discoveries"] = self._identify_technical_discoveries(elements)
        
        return analysis
    
    def _extract_themes(self, content: str) -> List[Dict[str, Any]]:
        """Extract dominant themes from story content"""
        # Technical theme patterns
        theme_patterns = {
            "authentication": r"\b(?:auth|login|password|token|security|jwt)\b",
            "database": r"\b(?:database|sql|query|table|migration|schema)\b",
            "api": r"\b(?:api|endpoint|rest|controller|service|response)\b",
            "testing": r"\b(?:test|testing|unit|integration|coverage|assert)\b",
            "performance": r"\b(?:performance|optimization|speed|latency|cache)\b",
            "ui": r"\b(?:ui|interface|component|react|angular|vue|css)\b",
            "deployment": r"\b(?:deploy|deployment|docker|kubernetes|aws|cloud)\b",
            "debugging": r"\b(?:debug|error|exception|fix|bug|issue)\b",
            "refactoring": r"\b(?:refactor|refactoring|cleanup|restructure|improve)\b",
            "documentation": r"\b(?:document|documentation|readme|wiki|guide)\b"
        }
        
        themes = []
        content_lower = content.lower()
        
        for theme_name, pattern in theme_patterns.items():
            matches = len(re.findall(pattern, content_lower, re.IGNORECASE))
            if matches >= 2:  # Require at least 2 mentions
                themes.append({
                    "theme": theme_name,
                    "mention_count": matches,
                    "relevance_score": min(1.0, matches / 10)  # Cap at 1.0
                })
        
        # Sort by relevance
        themes.sort(key=lambda x: x["relevance_score"], reverse=True)
        return themes[:5]  # Return top 5 themes
    
    def _identify_development_phases(self, elements: List[StoryElement]) -> List[Dict[str, Any]]:
        """Identify distinct phases in the development story"""
        if not elements:
            return []
        
        phases = []
        current_phase = None
        phase_elements = []
        
        for element in elements:
            # Determine phase based on element type and content
            phase_type = self._classify_development_phase(element)
            
            if current_phase is None or current_phase != phase_type:
                # Save previous phase
                if current_phase is not None and phase_elements:
                    phases.append({
                        "phase_type": current_phase,
                        "start_time": phase_elements[0].timestamp,
                        "end_time": phase_elements[-1].timestamp,
                        "element_count": len(phase_elements),
                        "key_activities": [elem.content[:100] + "..." 
                                         for elem in phase_elements[:3]]
                    })
                
                # Start new phase
                current_phase = phase_type
                phase_elements = [element]
            else:
                phase_elements.append(element)
        
        # Don't forget the last phase
        if current_phase is not None and phase_elements:
            phases.append({
                "phase_type": current_phase,
                "start_time": phase_elements[0].timestamp,
                "end_time": phase_elements[-1].timestamp,
                "element_count": len(phase_elements),
                "key_activities": [elem.content[:100] + "..." 
                                 for elem in phase_elements[:3]]
            })
        
        return phases
    
    def _classify_development_phase(self, element: StoryElement) -> str:
        """Classify what development phase an element belongs to"""
        content_lower = element.content.lower()
        
        # Phase classification patterns (more comprehensive)
        if re.search(r"\b(?:plan|planning|design|architecture|architect|spec|requirement|strategy|approach|outline)\b", content_lower):
            return "planning"
        elif re.search(r"\b(?:implement|implementing|code|coding|develop|developing|create|creating|build|building|add|adding|write)\b", content_lower):
            return "implementation"
        elif re.search(r"\b(?:test|testing|unit|integration|coverage|verify|assert|mock)\b", content_lower):
            return "testing"
        elif re.search(r"\b(?:debug|debugging|fix|fixing|error|bug|issue|problem|troubleshoot|investigate)\b", content_lower):
            return "debugging"
        elif re.search(r"\b(?:refactor|refactoring|cleanup|improve|optimize|restructure|reorganize)\b", content_lower):
            return "refactoring"
        elif re.search(r"\b(?:deploy|deployment|release|publish|production)\b", content_lower):
            return "deployment"
        elif re.search(r"\b(?:document|documentation|readme|guide|explain|describe)\b", content_lower):
            return "documentation"
        else:
            return "general_development"
    
    def _detect_complexity_indicators(self, elements: List[StoryElement]) -> List[Dict[str, Any]]:
        """Detect indicators of project complexity"""
        indicators = []
        
        # Count unique files involved
        unique_files = set()
        for element in elements:
            unique_files.update(element.related_files)
        
        if len(unique_files) > 10:
            indicators.append({
                "type": "high_file_complexity",
                "description": f"Work involved {len(unique_files)} different files",
                "impact": "medium"
            })
        
        # Look for error/debugging patterns
        error_count = sum(1 for elem in elements 
                         if re.search(r"\b(?:error|exception|bug|fix|debug)\b", 
                                    elem.content, re.IGNORECASE))
        
        if error_count > len(elements) * 0.3:  # More than 30% error-related
            indicators.append({
                "type": "high_debugging_activity",
                "description": f"{error_count} debugging-related activities",
                "impact": "high"
            })
        
        # Look for refactoring patterns
        refactor_count = sum(1 for elem in elements 
                           if re.search(r"\b(?:refactor|refactoring|restructure)\b", 
                                      elem.content, re.IGNORECASE))
        
        if refactor_count > 0:
            indicators.append({
                "type": "refactoring_activity",
                "description": f"{refactor_count} refactoring activities detected",
                "impact": "medium"
            })
        
        return indicators
    
    def _detect_collaboration_signals(self, elements: List[StoryElement]) -> List[Dict[str, Any]]:
        """Detect signs of collaborative work"""
        signals = []
        
        # Look for review/discussion patterns
        review_count = sum(1 for elem in elements 
                          if re.search(r"\b(?:review|discuss|feedback|comment|suggest)\b", 
                                     elem.content, re.IGNORECASE))
        
        if review_count > 0:
            signals.append({
                "type": "code_review_activity",
                "description": f"{review_count} review/discussion activities",
                "intensity": "medium" if review_count < 5 else "high"
            })
        
        # Look for merge/integration patterns
        merge_count = sum(1 for elem in elements 
                         if re.search(r"\b(?:merge|integration|conflict|branch)\b", 
                                    elem.content, re.IGNORECASE))
        
        if merge_count > 0:
            signals.append({
                "type": "integration_activity", 
                "description": f"{merge_count} merge/integration activities",
                "intensity": "low" if merge_count < 3 else "medium"
            })
        
        return signals
    
    def _identify_technical_discoveries(self, elements: List[StoryElement]) -> List[Dict[str, Any]]:
        """Identify technical insights and discoveries"""
        discoveries = []
        
        # Look for learning/insight patterns
        insight_patterns = [
            (r"\b(?:discovered|found|realized|learned|insight)\b", "discovery"),
            (r"\b(?:solution|approach|method|technique)\b", "solution"),
            (r"\b(?:pattern|best practice|optimization)\b", "optimization"),
            (r"\b(?:issue|problem|challenge|limitation)\b", "challenge")
        ]
        
        for pattern, discovery_type in insight_patterns:
            matches = []
            for elem in elements:
                if re.search(pattern, elem.content, re.IGNORECASE):
                    matches.append({
                        "timestamp": elem.timestamp,
                        "content": elem.content[:200] + "..." if len(elem.content) > 200 else elem.content,
                        "confidence": elem.confidence
                    })
            
            if matches:
                discoveries.append({
                    "type": discovery_type,
                    "count": len(matches),
                    "examples": matches[:3]  # Top 3 examples
                })
        
        return discoveries
    
    def _generate_narrative_text(self, 
                                elements: List[StoryElement], 
                                analysis: Dict[str, Any],
                                story_type: StoryType,
                                narrative_style: NarrativeStyle) -> str:
        """Generate the actual narrative text based on elements and analysis"""
        
        if story_type == StoryType.DEVELOPMENT_PROGRESS:
            return self._generate_development_progress_narrative(elements, analysis, narrative_style)
        elif story_type == StoryType.FEATURE_JOURNEY:
            return self._generate_feature_journey_narrative(elements, analysis, narrative_style)
        elif story_type == StoryType.PROBLEM_RESOLUTION:
            return self._generate_problem_resolution_narrative(elements, analysis, narrative_style)
        elif story_type == StoryType.LEARNING_EVOLUTION:
            return self._generate_learning_evolution_narrative(elements, analysis, narrative_style)
        else:
            return self._generate_generic_narrative(elements, analysis, narrative_style)
    
    def _generate_development_progress_narrative(self, 
                                               elements: List[StoryElement], 
                                               analysis: Dict[str, Any],
                                               style: NarrativeStyle) -> str:
        """Generate a development progress narrative"""
        
        if style == NarrativeStyle.EXECUTIVE:
            return self._generate_executive_progress_narrative(elements, analysis)
        elif style == NarrativeStyle.STORYTELLING:
            return self._generate_storytelling_progress_narrative(elements, analysis)
        else:  # Technical or Chronological
            return self._generate_technical_progress_narrative(elements, analysis)
    
    def _generate_executive_progress_narrative(self, elements: List[StoryElement], analysis: Dict[str, Any]) -> str:
        """Generate executive summary style narrative"""
        narrative = []
        
        # Executive Summary Header
        narrative.append("## Development Progress Summary")
        narrative.append(f"**Timeframe:** {analysis['time_span_hours']:.1f} hours of development activity")
        narrative.append(f"**Activities:** {analysis['element_count']} development activities tracked")
        narrative.append("")
        
        # Key Outcomes
        narrative.append("### Key Outcomes")
        if analysis["file_activity"]:
            top_files = list(analysis["file_activity"].keys())[:3]
            narrative.append(f"- **Primary Development Focus:** {', '.join(top_files)}")
        
        if analysis["development_phases"]:
            phase_types = [phase["phase_type"] for phase in analysis["development_phases"]]
            unique_phases = list(set(phase_types))
            narrative.append(f"- **Development Phases Completed:** {', '.join(unique_phases)}")
        
        if analysis["dominant_themes"]:
            top_themes = [theme["theme"] for theme in analysis["dominant_themes"][:3]]
            narrative.append(f"- **Technical Areas:** {', '.join(top_themes)}")
        
        # Risk Assessment
        narrative.append("")
        narrative.append("### Risk Assessment")
        complexity_indicators = analysis.get("complexity_indicators", [])
        if complexity_indicators:
            high_impact = [ind for ind in complexity_indicators if ind.get("impact") == "high"]
            if high_impact:
                narrative.append("- **High Risk Areas Identified:** Significant debugging activity detected")
            else:
                narrative.append("- **Risk Level:** Moderate - normal development complexity")
        else:
            narrative.append("- **Risk Level:** Low - development proceeding smoothly")
        
        # Collaboration Health
        collaboration_signals = analysis.get("collaboration_signals", [])
        if collaboration_signals:
            narrative.append("- **Team Collaboration:** Active code review and integration activities")
        
        return "\n".join(narrative)
    
    def _generate_storytelling_progress_narrative(self, elements: List[StoryElement], analysis: Dict[str, Any]) -> str:
        """Generate engaging storytelling style narrative"""
        narrative = []
        
        # Story Opening
        if analysis["time_span_hours"] < 24:
            time_desc = "a focused development session"
        elif analysis["time_span_hours"] < 168:  # 1 week
            time_desc = "an intensive week of development"
        else:
            time_desc = "an extended development journey"
        
        narrative.append(f"## The Story of {time_desc.title()}")
        narrative.append("")
        
        # Set the scene
        if analysis["dominant_themes"]:
            main_theme = analysis["dominant_themes"][0]["theme"]
            narrative.append(f"This is the story of how {main_theme} came to life in our codebase. ")
        else:
            narrative.append("This is the story of a development journey. ")
        
        narrative.append(f"Over {analysis['time_span_hours']:.1f} hours, our development team navigated ")
        narrative.append(f"through {analysis['element_count']} different activities, each contributing ")
        narrative.append("to the evolution of the system.")
        narrative.append("")
        
        # Journey through phases
        narrative.append("### The Development Journey")
        phases = analysis.get("development_phases", [])
        if phases:
            for i, phase in enumerate(phases):
                phase_num = i + 1
                narrative.append(f"**Chapter {phase_num}: The {phase['phase_type'].title()} Phase**")
                narrative.append(f"Our journey began with {phase['phase_type']} activities. ")
                if phase["key_activities"]:
                    narrative.append(f"Key moments included: {phase['key_activities'][0]}")
                narrative.append("")
        
        # Challenges and discoveries
        discoveries = analysis.get("technical_discoveries", [])
        if discoveries:
            narrative.append("### Discoveries Along the Way")
            for discovery in discoveries[:2]:  # Top 2 discoveries
                if discovery["examples"]:
                    narrative.append(f"- **{discovery['type'].title()}:** {discovery['examples'][0]['content']}")
            narrative.append("")
        
        # The resolution
        narrative.append("### Where We Are Now")
        if analysis["file_activity"]:
            most_active_file = list(analysis["file_activity"].keys())[0]
            narrative.append(f"The development story culminated with significant work on {most_active_file}, ")
            narrative.append("representing the heart of our technical progress.")
        
        return "\n".join(narrative)
    
    def _generate_technical_progress_narrative(self, elements: List[StoryElement], analysis: Dict[str, Any]) -> str:
        """Generate technical style narrative"""
        narrative = []
        
        # Technical Summary
        narrative.append("## Technical Development Report")
        narrative.append("")
        narrative.append("### Overview")
        narrative.append(f"- **Duration:** {analysis['time_span_hours']:.2f} hours")
        narrative.append(f"- **Activities:** {analysis['element_count']} tracked events")
        narrative.append(f"- **Files Modified:** {len(analysis['file_activity'])} files")
        narrative.append("")
        
        # File Activity Analysis
        if analysis["file_activity"]:
            narrative.append("### File Activity Analysis")
            for file, activity_count in list(analysis["file_activity"].items())[:5]:
                narrative.append(f"- `{file}`: {activity_count} activities")
            narrative.append("")
        
        # Phase Breakdown
        phases = analysis.get("development_phases", [])
        if phases:
            narrative.append("### Development Phase Breakdown")
            for phase in phases:
                duration = (phase["end_time"] - phase["start_time"]).total_seconds() / 3600
                narrative.append(f"- **{phase['phase_type'].title()}:** {duration:.1f} hours, {phase['element_count']} activities")
            narrative.append("")
        
        # Technical Themes
        if analysis["dominant_themes"]:
            narrative.append("### Technical Focus Areas")
            for theme in analysis["dominant_themes"]:
                percentage = theme["relevance_score"] * 100
                narrative.append(f"- **{theme['theme'].title()}:** {percentage:.0f}% relevance ({theme['mention_count']} mentions)")
            narrative.append("")
        
        # Complexity Assessment
        complexity_indicators = analysis.get("complexity_indicators", [])
        if complexity_indicators:
            narrative.append("### Complexity Indicators")
            for indicator in complexity_indicators:
                narrative.append(f"- **{indicator['type'].replace('_', ' ').title()}:** {indicator['description']}")
            narrative.append("")
        
        # Discoveries and Insights
        discoveries = analysis.get("technical_discoveries", [])
        if discoveries:
            narrative.append("### Technical Discoveries")
            for discovery in discoveries:
                narrative.append(f"- **{discovery['type'].title()}:** {discovery['count']} instances identified")
            narrative.append("")
        
        return "\n".join(narrative)
    
    def _generate_feature_journey_narrative(self, elements: List[StoryElement], analysis: Dict[str, Any], style: NarrativeStyle) -> str:
        """Generate feature development journey narrative"""
        narrative = []
        narrative.append("## Feature Development Journey")
        narrative.append("")
        narrative.append("This narrative tracks the development of a specific feature through its lifecycle.")
        # Implementation would be similar to progress narrative but focused on feature evolution
        return "\n".join(narrative)
    
    def _generate_problem_resolution_narrative(self, elements: List[StoryElement], analysis: Dict[str, Any], style: NarrativeStyle) -> str:
        """Generate problem resolution narrative"""
        narrative = []
        narrative.append("## Problem Resolution Story")
        narrative.append("")
        narrative.append("This narrative chronicles the investigation and resolution of a technical challenge.")
        # Implementation would focus on debugging patterns and solution discovery
        return "\n".join(narrative)
    
    def _generate_learning_evolution_narrative(self, elements: List[StoryElement], analysis: Dict[str, Any], style: NarrativeStyle) -> str:
        """Generate learning evolution narrative"""
        narrative = []
        narrative.append("## Learning Evolution Story")
        narrative.append("")
        narrative.append("This narrative shows how knowledge and patterns evolved during development.")
        # Implementation would focus on pattern learning and knowledge accumulation
        return "\n".join(narrative)
    
    def _generate_generic_narrative(self, elements: List[StoryElement], analysis: Dict[str, Any], style: NarrativeStyle) -> str:
        """Generate generic narrative for unspecified story types"""
        return self._generate_technical_progress_narrative(elements, analysis)
    
    def _generate_story_title(self, analysis: Dict[str, Any], story_type: StoryType) -> str:
        """Generate an appropriate title for the story"""
        if story_type == StoryType.DEVELOPMENT_PROGRESS:
            if analysis["dominant_themes"]:
                main_theme = analysis["dominant_themes"][0]["theme"]
                return f"Development Progress: {main_theme.title()} Implementation"
            else:
                return f"Development Progress: {analysis['element_count']} Activities"
        elif story_type == StoryType.FEATURE_JOURNEY:
            return "Feature Development Journey"
        elif story_type == StoryType.PROBLEM_RESOLUTION:
            return "Problem Resolution Chronicle"
        elif story_type == StoryType.LEARNING_EVOLUTION:
            return "Knowledge Evolution Story"
        else:
            return "Development Narrative"
    
    def _calculate_narrative_confidence(self, elements: List[StoryElement], analysis: Dict[str, Any]) -> float:
        """Calculate confidence score for the generated narrative"""
        base_confidence = 0.6
        
        # Boost confidence based on number of elements
        element_boost = min(0.2, len(elements) / 50)  # Up to 0.2 boost for 50+ elements
        
        # Boost confidence based on element confidence
        avg_element_confidence = sum(elem.confidence for elem in elements) / len(elements) if elements else 0.5
        confidence_boost = (avg_element_confidence - 0.5) * 0.4
        
        # Boost confidence based on analysis richness
        analysis_boost = 0.0
        if analysis.get("dominant_themes"):
            analysis_boost += 0.1
        if analysis.get("development_phases"):
            analysis_boost += 0.1
        if analysis.get("file_activity"):
            analysis_boost += 0.05
        
        total_confidence = base_confidence + element_boost + confidence_boost + analysis_boost
        return min(0.95, max(0.3, total_confidence))  # Clamp between 0.3 and 0.95
    
    def _create_empty_narrative(self, story_type: StoryType, style: NarrativeStyle, time_range: Tuple[datetime, datetime]) -> DevelopmentNarrative:
        """Create a narrative for when no story elements are found"""
        start_time, end_time = time_range
        duration = (end_time - start_time).total_seconds() / 3600
        
        empty_narrative = f"""
## No Development Activity Found

### Time Period Analyzed
- **Start:** {start_time.strftime('%Y-%m-%d %H:%M')}
- **End:** {end_time.strftime('%Y-%m-%d %H:%M')}
- **Duration:** {duration:.1f} hours

### Summary
No development activities were recorded during this time period. This could indicate:
- No active development work
- Activities not yet captured by the narrative intelligence system
- Time period outside of normal development hours

### Recommendation
Consider expanding the time range or checking if story elements are being properly captured.
"""
        
        return DevelopmentNarrative(
            narrative_id=None,
            title="No Activity Found",
            story_type=story_type,
            narrative_style=style,
            story_elements=[],
            generated_narrative=empty_narrative.strip(),
            metadata={"element_count": 0, "time_span_hours": duration},
            created_at=datetime.now(),
            confidence_score=0.1
        )
    
    
    def _serialize_story_element(self, element: StoryElement) -> Dict[str, Any]:
        """Serialize a story element for JSON storage"""
        return {
            'element_id': element.element_id,
            'timestamp': element.timestamp.isoformat(),
            'element_type': element.element_type,
            'content': element.content,
            'confidence': element.confidence,
            'related_files': element.related_files,
            'context_tags': element.context_tags,
            'metadata': element.metadata
        }
    
    def _store_narrative(self, narrative: DevelopmentNarrative) -> bool:
        """Store generated narrative in database"""
        try:
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT OR REPLACE INTO development_narratives
                    (narrative_id, title, story_type, narrative_style, story_elements,
                     generated_narrative, metadata, confidence_score, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    narrative.narrative_id,
                    narrative.title,
                    narrative.story_type.value,
                    narrative.narrative_style.value,
                    json.dumps([self._serialize_story_element(elem) for elem in narrative.story_elements]),
                    narrative.generated_narrative,
                    json.dumps(narrative.metadata, default=str),
                    narrative.confidence_score,
                    narrative.created_at.isoformat()
                ))
                
                conn.commit()
                return True
                
        except sqlite3.Error as e:
            logger.error(f"Failed to store narrative: {e}")
            return False
    
    def get_recent_narratives(self, limit: int = 10) -> List[DevelopmentNarrative]:
        """Get recently generated narratives"""
        try:
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT narrative_id, title, story_type, narrative_style, story_elements,
                           generated_narrative, metadata, confidence_score, created_at
                    FROM development_narratives 
                    ORDER BY created_at DESC 
                    LIMIT ?
                """, (limit,))
                
                narratives = []
                for row in cursor.fetchall():
                    # Parse story elements
                    elements_data = json.loads(row[4])
                    story_elements = [StoryElement(**elem_dict) for elem_dict in elements_data]
                    
                    # Convert timestamp strings back to datetime objects
                    for elem in story_elements:
                        if isinstance(elem.timestamp, str):
                            elem.timestamp = datetime.fromisoformat(elem.timestamp)
                    
                    narrative = DevelopmentNarrative(
                        narrative_id=row[0],
                        title=row[1],
                        story_type=StoryType(row[2]),
                        narrative_style=NarrativeStyle(row[3]),
                        story_elements=story_elements,
                        generated_narrative=row[5],
                        metadata=json.loads(row[6]),
                        confidence_score=row[7],
                        created_at=datetime.fromisoformat(row[8])
                    )
                    narratives.append(narrative)
                
                return narratives
                
        except sqlite3.Error as e:
            logger.error(f"Failed to get recent narratives: {e}")
            return []
    
    def get_narrative_statistics(self) -> Dict[str, Any]:
        """Get statistics about narrative generation"""
        try:
            with sqlite3.connect(self.database_path) as conn:
                cursor = conn.cursor()
                
                # Get narrative counts by type
                cursor.execute("""
                    SELECT story_type, COUNT(*) as count, AVG(confidence_score) as avg_confidence
                    FROM development_narratives 
                    GROUP BY story_type
                """)
                narrative_stats = {row[0]: {"count": row[1], "avg_confidence": row[2]} 
                                 for row in cursor.fetchall()}
                
                # Get story element statistics
                cursor.execute("""
                    SELECT element_type, COUNT(*) as count
                    FROM story_elements 
                    GROUP BY element_type
                """)
                element_stats = {row[0]: row[1] for row in cursor.fetchall()}
                
                # Get total counts
                cursor.execute("SELECT COUNT(*) FROM development_narratives")
                total_narratives = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM story_elements")
                total_elements = cursor.fetchone()[0]
                
                return {
                    "narrative_statistics": narrative_stats,
                    "element_statistics": element_stats,
                    "total_narratives": total_narratives,
                    "total_story_elements": total_elements,
                    "narrative_intelligence_status": "operational"
                }
                
        except sqlite3.Error as e:
            logger.error(f"Failed to get narrative statistics: {e}")
            return {"narrative_intelligence_status": "error", "error": str(e)}
    
    def import_conversation_data(self, conversation_data: Dict[str, Any]) -> bool:
        """Import conversation data and create story elements"""
        try:
            # Extract relevant information from conversation
            conversation_id = conversation_data.get("conversation_id", f"conv_{uuid.uuid4().hex[:8]}")
            messages = conversation_data.get("messages", [])
            timestamp = conversation_data.get("timestamp")
            
            if isinstance(timestamp, str):
                timestamp = datetime.fromisoformat(timestamp)
            elif timestamp is None:
                timestamp = datetime.now()
            
            # Create story element from conversation
            content = " ".join([msg.get("content", "") for msg in messages])
            related_files = self._extract_files_from_content(content)
            context_tags = self._extract_context_tags_from_content(content)
            
            element = StoryElement(
                element_id=f"conv_elem_{conversation_id}",
                timestamp=timestamp,
                element_type="conversation",
                content=content[:1000] + "..." if len(content) > 1000 else content,  # Truncate long content
                confidence=0.8,
                related_files=related_files,
                context_tags=context_tags
            )
            
            return self.add_story_element(element)
            
        except Exception as e:
            logger.error(f"Failed to import conversation data: {e}")
            return False
    
    def _extract_files_from_content(self, content: str) -> List[str]:
        """Extract file mentions from conversation content"""
        file_patterns = [
            r'\b\w+\.[a-zA-Z]{2,4}\b',  # Files with extensions
            r'\b\w+Controller\b',        # Controller classes
            r'\b\w+Service\b',          # Service classes
            r'\b\w+Model\b',            # Model classes
            r'\b\w+Component\b',        # Component classes
            r'\b\w+Tests?\b'            # Test classes
        ]
        
        files = set()
        for pattern in file_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            files.update(matches)
        
        return list(files)[:10]  # Limit to prevent noise
    
    def _extract_context_tags_from_content(self, content: str) -> List[str]:
        """Extract context tags from conversation content"""
        tag_patterns = {
            'bug_fix': r'\b(?:bug|error|fix|debug|issue)\b',
            'feature': r'\b(?:feature|implement|add|create|new)\b',
            'refactor': r'\b(?:refactor|cleanup|improve|optimize)\b',
            'test': r'\b(?:test|testing|unit|integration|coverage)\b',
            'documentation': r'\b(?:document|documentation|readme|guide)\b',
            'performance': r'\b(?:performance|speed|optimization|cache)\b',
            'security': r'\b(?:security|auth|authentication|permission)\b',
            'api': r'\b(?:api|endpoint|rest|graphql)\b',
            'database': r'\b(?:database|sql|query|migration|schema)\b',
            'ui': r'\b(?:ui|interface|component|frontend|styling)\b'
        }
        
        tags = []
        content_lower = content.lower()
        
        for tag, pattern in tag_patterns.items():
            if re.search(pattern, content_lower):
                tags.append(tag)
        
        return tags