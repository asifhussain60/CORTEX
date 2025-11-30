"""
CORTEX 3.0 - Conversation Pipeline Collector
============================================

Captures and processes conversations for CORTEX memory system.
Integrates with Tier 1 (working memory) and conversation captures.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.

Feature: Task 4 - Conversation Pipeline Integration
Effort: 3 hours (pipeline setup + processing)
Target: Real-time conversation capture with quality analysis
"""

from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime, timezone
import json
import sqlite3
import re
from pathlib import Path
import hashlib
from enum import Enum

from .base_collector import BaseCollector, CollectorMetric, CollectorPriority, CollectorStatus


class ConversationQuality(Enum):
    """Conversation quality levels for strategic value"""
    EXCELLENT = "excellent"      # 9-10: Strategic patterns, complex implementations
    GOOD = "good"               # 7-8: Useful patterns, solid implementations  
    FAIR = "fair"               # 5-6: Standard interactions
    POOR = "poor"               # 3-4: Simple Q&A
    MINIMAL = "minimal"         # 1-2: Very basic interactions


@dataclass
class ConversationMetadata:
    """Metadata extracted from conversation content"""
    participant_count: int = 0
    message_count: int = 0
    code_snippets: int = 0
    files_mentioned: Set[str] = field(default_factory=set)
    technologies: Set[str] = field(default_factory=set)
    intents: Set[str] = field(default_factory=set)
    complexity_indicators: Set[str] = field(default_factory=set)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'participant_count': self.participant_count,
            'message_count': self.message_count,
            'code_snippets': self.code_snippets,
            'files_mentioned': list(self.files_mentioned),
            'technologies': list(self.technologies),
            'intents': list(self.intents),
            'complexity_indicators': list(self.complexity_indicators)
        }


@dataclass
class ProcessedConversation:
    """Fully processed conversation ready for storage"""
    conversation_id: str
    title: str
    participants: List[str]
    messages: List[Dict[str, Any]]
    metadata: ConversationMetadata
    quality_score: float
    quality_level: ConversationQuality
    strategic_value: bool
    timestamp: datetime
    source_file: Optional[str] = None
    processing_notes: List[str] = field(default_factory=list)


class ConversationCollector(BaseCollector):
    """
    Conversation Pipeline Collector
    
    Responsibilities:
    1. Monitor conversation-captures/ for new files
    2. Process conversation content (quality analysis)
    3. Extract metadata and semantic elements
    4. Store in Tier 1 database
    5. Archive processed files to conversation-vault/
    """
    
    def __init__(self, brain_path: str):
        super().__init__(
            collector_id="conversation_pipeline",
            name="Conversation Pipeline Collector",
            priority=CollectorPriority.HIGH,  # Critical for memory system
            collection_interval_seconds=10.0,  # Check every 10 seconds
            brain_path=brain_path
        )
        
        # Paths setup
        self.captures_path = Path(brain_path) / "conversation-captures"
        self.vault_path = Path(brain_path) / "conversation-vault"
        self.tier1_db_path = Path(brain_path) / "tier1-working-memory.db"
        
        # Processing state
        self.processed_files: Set[str] = set()
        self.quality_thresholds = {
            ConversationQuality.EXCELLENT: 9.0,
            ConversationQuality.GOOD: 7.0,
            ConversationQuality.FAIR: 5.0,
            ConversationQuality.POOR: 3.0,
            ConversationQuality.MINIMAL: 0.0
        }
        
        # Technology patterns for metadata extraction
        self.tech_patterns = {
            'python': r'\b(?:python|\.py|pip|pytest|django|flask)\b',
            'javascript': r'\b(?:javascript|js|node|npm|react|vue|angular)\b',
            'csharp': r'\b(?:c#|csharp|\.cs|dotnet|visual studio)\b',
            'sql': r'\b(?:sql|sqlite|postgres|mysql|database)\b',
            'web': r'\b(?:html|css|http|api|rest|graphql)\b',
            'git': r'\b(?:git|github|commit|branch|pull request|pr)\b',
            'docker': r'\b(?:docker|container|dockerfile|kubernetes)\b',
            'cloud': r'\b(?:aws|azure|gcp|cloud|serverless)\b'
        }
        
        # File patterns for extraction
        self.file_patterns = [
            r'(?:\w+\.(?:py|js|ts|cs|java|cpp|h|sql|md|yaml|json|xml))',
            r'(?:/[\w/-]+\.(?:py|js|ts|cs|java|cpp|h|sql|md|yaml|json|xml))',
            r'(?:\.[\w/-]+\.(?:py|js|ts|cs|java|cpp|h|sql|md|yaml|json|xml))'
        ]
    
    def start(self) -> bool:
        """Start conversation pipeline collector"""
        if not super().start():
            return False
            
        try:
            # Ensure directories exist
            self.captures_path.mkdir(exist_ok=True)
            self.vault_path.mkdir(exist_ok=True)
            
            # Create vault year/month structure
            now = datetime.now()
            year_path = self.vault_path / str(now.year)
            month_path = year_path / f"{now.month:02d}"
            month_path.mkdir(parents=True, exist_ok=True)
            
            # Initialize Tier 1 database if needed
            self._init_tier1_database()
            
            self.status = CollectorStatus.ACTIVE
            self.logger.info(f"Conversation pipeline collector started")
            return True
            
        except Exception as e:
            self.last_error = str(e)
            self.error_count += 1
            self.status = CollectorStatus.ERROR
            self.logger.error(f"Failed to start conversation collector: {e}")
            return False
    
    # The collect() method is inherited from BaseCollector
    # It calls our _collect_metrics() method which delegates to _collect_conversation_metrics()
    
    def _find_new_conversation_files(self) -> List[Path]:
        """Find new conversation files to process"""
        new_files = []
        
        # Look for .md files in captures directory
        for md_file in self.captures_path.glob("*.md"):
            # Skip README and already processed files
            if md_file.name == "README.md":
                continue
                
            if str(md_file) in self.processed_files:
                continue
            
            # Check if file has content (not just empty placeholder)
            if md_file.stat().st_size > 100:  # More than just header
                new_files.append(md_file)
        
        return new_files
    
    def _process_conversation_file(self, file_path: Path) -> Optional[ProcessedConversation]:
        """
        Process a single conversation file
        
        Args:
            file_path: Path to conversation file
            
        Returns:
            ProcessedConversation or None if processing failed
        """
        try:
            content = file_path.read_text(encoding='utf-8')
            
            # Extract basic info
            conversation_id = self._generate_conversation_id(file_path, content)
            title = self._extract_title(file_path, content)
            participants = self._extract_participants(content)
            messages = self._extract_messages(content)
            
            # Extract metadata
            metadata = self._extract_metadata(content)
            
            # Calculate quality score
            quality_score = self._calculate_quality_score(content, metadata, messages)
            quality_level = self._determine_quality_level(quality_score)
            
            # Determine strategic value
            strategic_value = quality_score >= 7.0 and (
                len(metadata.complexity_indicators) > 0 or
                metadata.code_snippets > 2 or
                metadata.message_count > 10
            )
            
            return ProcessedConversation(
                conversation_id=conversation_id,
                title=title,
                participants=participants,
                messages=messages,
                metadata=metadata,
                quality_score=quality_score,
                quality_level=quality_level,
                strategic_value=strategic_value,
                timestamp=datetime.now(timezone.utc),
                source_file=str(file_path),
                processing_notes=[]
            )
            
        except Exception as e:
            self.logger.error(f"Failed to process conversation file {file_path}: {e}")
            return None
    
    def _extract_metadata(self, content: str) -> ConversationMetadata:
        """Extract metadata from conversation content"""
        metadata = ConversationMetadata()
        
        # Count participants
        metadata.participant_count = len(set(re.findall(r'^(\w+):', content, re.MULTILINE)))
        
        # Count messages
        metadata.message_count = len(re.findall(r'^(\w+):', content, re.MULTILINE))
        
        # Count code snippets
        metadata.code_snippets = len(re.findall(r'```[\s\S]*?```', content))
        
        # Extract file mentions
        for pattern in self.file_patterns:
            files = re.findall(pattern, content, re.IGNORECASE)
            metadata.files_mentioned.update(files)
        
        # Extract technologies
        for tech, pattern in self.tech_patterns.items():
            if re.search(pattern, content, re.IGNORECASE):
                metadata.technologies.add(tech)
        
        # Extract intents (basic patterns)
        intent_patterns = {
            'implementation': r'\b(?:implement|create|add|build)\b',
            'debugging': r'\b(?:debug|fix|error|bug|issue)\b',
            'planning': r'\b(?:plan|design|architecture|strategy)\b',
            'testing': r'\b(?:test|verify|validate|check)\b',
            'documentation': r'\b(?:document|explain|describe)\b'
        }
        
        for intent, pattern in intent_patterns.items():
            if re.search(pattern, content, re.IGNORECASE):
                metadata.intents.add(intent)
        
        # Complexity indicators
        complexity_patterns = {
            'multi_phase': r'\b(?:phase|stage|milestone)\b.*\b(?:phase|stage|milestone)\b',
            'architecture': r'\b(?:architecture|design pattern|framework)\b',
            'integration': r'\b(?:integrate|connect|api|service)\b',
            'performance': r'\b(?:optimize|performance|scalability)\b',
            'security': r'\b(?:security|authentication|authorization|encrypt)\b'
        }
        
        for indicator, pattern in complexity_patterns.items():
            if re.search(pattern, content, re.IGNORECASE):
                metadata.complexity_indicators.add(indicator)
        
        return metadata
    
    def _calculate_quality_score(self, content: str, metadata: ConversationMetadata, messages: List[Dict]) -> float:
        """
        Calculate quality score for conversation (0-10)
        
        Scoring factors:
        - Message depth and length
        - Technical complexity
        - Code examples
        - Strategic planning
        - Problem-solution pairs
        """
        score = 0.0
        
        # Base score from message count and length
        avg_message_length = len(content) / max(metadata.message_count, 1)
        if avg_message_length > 200:
            score += 2.0
        elif avg_message_length > 100:
            score += 1.0
        
        # Technical complexity
        score += min(len(metadata.technologies) * 0.5, 2.0)
        score += min(len(metadata.complexity_indicators) * 0.7, 2.5)
        
        # Code examples
        if metadata.code_snippets > 3:
            score += 2.0
        elif metadata.code_snippets > 1:
            score += 1.0
        elif metadata.code_snippets > 0:
            score += 0.5
        
        # Strategic indicators
        if 'planning' in metadata.intents:
            score += 1.0
        if 'architecture' in metadata.complexity_indicators:
            score += 1.5
        
        # Multi-turn conversations are more valuable
        if metadata.message_count > 15:
            score += 1.5
        elif metadata.message_count > 8:
            score += 1.0
        
        # Cap at 10.0
        return min(score, 10.0)
    
    def _determine_quality_level(self, score: float) -> ConversationQuality:
        """Determine quality level from score"""
        for level, threshold in self.quality_thresholds.items():
            if score >= threshold:
                return level
        return ConversationQuality.MINIMAL
    
    def _generate_conversation_id(self, file_path: Path, content: str) -> str:
        """Generate unique conversation ID"""
        # Use file path + content hash for uniqueness
        content_hash = hashlib.md5(content.encode()).hexdigest()[:8]
        return f"conv_{file_path.stem}_{content_hash}"
    
    def _extract_title(self, file_path: Path, content: str) -> str:
        """Extract conversation title"""
        # Try to find title in content
        title_match = re.search(r'^# (.+)', content, re.MULTILINE)
        if title_match:
            return title_match.group(1).strip()
        
        # Fall back to filename
        return file_path.stem.replace('-', ' ').title()
    
    def _extract_participants(self, content: str) -> List[str]:
        """Extract conversation participants"""
        participants = set()
        for match in re.finditer(r'^(\w+):', content, re.MULTILINE):
            participants.add(match.group(1))
        return list(participants)
    
    def _extract_messages(self, content: str) -> List[Dict[str, Any]]:
        """Extract structured messages from conversation"""
        messages = []
        
        # Split by participant markers
        current_speaker = None
        current_message = []
        
        for line in content.split('\n'):
            speaker_match = re.match(r'^(\w+):\s*(.*)', line)
            if speaker_match:
                # Save previous message
                if current_speaker and current_message:
                    messages.append({
                        'speaker': current_speaker,
                        'content': '\n'.join(current_message).strip(),
                        'timestamp': None  # Would need to be extracted if available
                    })
                
                # Start new message
                current_speaker = speaker_match.group(1)
                current_message = [speaker_match.group(2)] if speaker_match.group(2) else []
            else:
                # Continue current message
                if current_speaker:
                    current_message.append(line)
        
        # Save final message
        if current_speaker and current_message:
            messages.append({
                'speaker': current_speaker,
                'content': '\n'.join(current_message).strip(),
                'timestamp': None
            })
        
        return messages
    
    def _init_tier1_database(self):
        """Initialize Tier 1 database for conversations"""
        try:
            conn = sqlite3.connect(self.tier1_db_path)
            cursor = conn.cursor()
            
            # Create conversations table if not exists
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS conversations (
                    conversation_id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    participants TEXT NOT NULL,  -- JSON array
                    message_count INTEGER NOT NULL,
                    quality_score REAL NOT NULL,
                    quality_level TEXT NOT NULL,
                    strategic_value BOOLEAN NOT NULL,
                    metadata TEXT NOT NULL,      -- JSON object
                    messages TEXT NOT NULL,      -- JSON array
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    source_file TEXT
                )
            ''')
            
            # Create index for performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_conversations_created_at ON conversations(created_at)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_conversations_quality ON conversations(quality_score)')
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Tier 1 database: {e}")
            raise
    
    def _store_conversation(self, conversation: ProcessedConversation):
        """Store conversation in Tier 1 database"""
        try:
            conn = sqlite3.connect(self.tier1_db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO conversations (
                    conversation_id, title, participants, message_count,
                    quality_score, quality_level, strategic_value,
                    metadata, messages, source_file
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                conversation.conversation_id,
                conversation.title,
                json.dumps(conversation.participants),
                conversation.metadata.message_count,
                conversation.quality_score,
                conversation.quality_level.value,
                conversation.strategic_value,
                json.dumps(conversation.metadata.to_dict()),
                json.dumps(conversation.messages),
                conversation.source_file
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Failed to store conversation: {e}")
            raise
    
    def _archive_conversation(self, source_file: Path, conversation: ProcessedConversation):
        """Archive conversation to vault with metadata"""
        try:
            # Create archive path
            timestamp = conversation.timestamp
            year_path = self.vault_path / str(timestamp.year)
            month_path = year_path / f"{timestamp.month:02d}"
            month_path.mkdir(parents=True, exist_ok=True)
            
            # Archive filename with quality indicator
            quality_prefix = conversation.quality_level.value[:1].upper()  # E, G, F, P, M
            archive_filename = f"{timestamp.strftime('%Y-%m-%d')}-{quality_prefix}-{source_file.stem}.md"
            archive_path = month_path / archive_filename
            
            # Create archive content with metadata header
            archive_content = f"""---
conversation_id: {conversation.conversation_id}
title: {conversation.title}
participants: {conversation.participants}
quality_score: {conversation.quality_score}
quality_level: {conversation.quality_level.value}
strategic_value: {conversation.strategic_value}
message_count: {conversation.metadata.message_count}
code_snippets: {conversation.metadata.code_snippets}
technologies: {list(conversation.metadata.technologies)}
intents: {list(conversation.metadata.intents)}
processed_at: {conversation.timestamp.isoformat()}
source_file: {conversation.source_file}
---

{source_file.read_text(encoding='utf-8')}
"""
            
            # Write archive
            archive_path.write_text(archive_content, encoding='utf-8')
            
            # Remove original file
            source_file.unlink()
            
            self.logger.info(f"Archived conversation to {archive_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to archive conversation: {e}")
            raise
    
    def _create_conversation_metrics(self, conversation: ProcessedConversation) -> List[CollectorMetric]:
        """Create metrics for processed conversation"""
        timestamp = datetime.now(timezone.utc)
        base_tags = {
            "collector": self.collector_id,
            "conversation_id": conversation.conversation_id,
            "quality_level": conversation.quality_level.value
        }
        
        metrics = [
            CollectorMetric(
                name="conversation_quality_score",
                value=conversation.quality_score,
                timestamp=timestamp,
                tags={**base_tags, "metric_type": "quality"}
            ),
            CollectorMetric(
                name="conversation_message_count",
                value=conversation.metadata.message_count,
                timestamp=timestamp,
                tags={**base_tags, "metric_type": "size"}
            ),
            CollectorMetric(
                name="conversation_code_snippets",
                value=conversation.metadata.code_snippets,
                timestamp=timestamp,
                tags={**base_tags, "metric_type": "technical"}
            ),
            CollectorMetric(
                name="conversation_strategic_value",
                value=int(conversation.strategic_value),
                timestamp=timestamp,
                tags={**base_tags, "metric_type": "strategic"}
            )
        ]
        
        # Add technology metrics
        for tech in conversation.metadata.technologies:
            metrics.append(CollectorMetric(
                name="conversation_technology_mention",
                value=1,
                timestamp=timestamp,
                tags={**base_tags, "technology": tech, "metric_type": "technology"}
            ))
        
        return metrics
    
    def stop(self) -> bool:
        """Stop conversation collector"""
        if super().stop():
            self.logger.info("Conversation pipeline collector stopped")
            return True
        return False
    
    def _collect_metrics(self) -> List[CollectorMetric]:
        """
        Implement abstract method from BaseCollector
        
        Returns:
            List[CollectorMetric]: Current metrics from conversation processing
        """
        # This is called by the base collect() method
        # We delegate to our main collect logic
        return self._collect_conversation_metrics()
    
    def _collect_conversation_metrics(self) -> List[CollectorMetric]:
        """
        Internal method to collect conversation metrics
        
        Returns:
            List[CollectorMetric]: Metrics about conversation processing
        """
        metrics = []
        
        try:
            # Find new conversation files
            new_files = self._find_new_conversation_files()
            
            if not new_files:
                # No new files, return basic status metric
                metrics.append(CollectorMetric(
                    name="conversations_pending",
                    value=0,
                    timestamp=datetime.now(timezone.utc),
                    tags={"collector": self.collector_id}
                ))
                return metrics
            
            # Process each new conversation
            processed_count = 0
            error_count = 0
            
            for file_path in new_files:
                try:
                    processed_conversation = self._process_conversation_file(file_path)
                    if processed_conversation:
                        # Store in Tier 1 database
                        self._store_conversation(processed_conversation)
                        
                        # Archive to vault
                        self._archive_conversation(file_path, processed_conversation)
                        
                        # Mark as processed
                        self.processed_files.add(str(file_path))
                        processed_count += 1
                        
                        # Add metrics for this conversation
                        metrics.extend(self._create_conversation_metrics(processed_conversation))
                        
                        self.logger.info(f"Processed conversation: {processed_conversation.title}")
                    
                except Exception as e:
                    error_count += 1
                    self.logger.error(f"Failed to process {file_path}: {e}")
            
            # Summary metrics
            metrics.append(CollectorMetric(
                name="conversations_processed",
                value=processed_count,
                timestamp=datetime.now(timezone.utc),
                tags={"collector": self.collector_id, "batch": "current"}
            ))
            
            if error_count > 0:
                metrics.append(CollectorMetric(
                    name="conversation_processing_errors", 
                    value=error_count,
                    timestamp=datetime.now(timezone.utc),
                    tags={"collector": self.collector_id, "severity": "error"}
                ))
            
            self.metrics_collected += len(metrics)
            self.last_collection = datetime.now(timezone.utc)
            
        except Exception as e:
            self.error_count += 1
            self.last_error = str(e)
            self.logger.error(f"Conversation collection failed: {e}")
            
            # Error metric
            metrics.append(CollectorMetric(
                name="collector_error",
                value=str(e),
                timestamp=datetime.now(timezone.utc),
                tags={"collector": self.collector_id, "error_type": "collection_failure"}
            ))
        
        return metrics