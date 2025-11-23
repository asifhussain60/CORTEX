"""
Feedback Collector - Gathers CORTEX Usage Data

Collects feedback about CORTEX functionality, errors, and user experience.
Automatically anonymizes sensitive information before storage.

Safety Features:
- Privacy Protection: Removes file paths, usernames, emails
- Selective Collection: Only gathers non-sensitive metrics
- Opt-In: User controls what data is collected

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary
"""

import hashlib
import logging
import platform
import re
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
import json


logger = logging.getLogger(__name__)


class FeedbackCategory(Enum):
    """Categories for feedback classification."""
    BUG = "bug"  # Something doesn't work
    FEATURE_REQUEST = "feature_request"  # New capability request
    IMPROVEMENT = "improvement"  # Enhancement to existing feature
    DOCUMENTATION = "documentation"  # Docs issue
    PERFORMANCE = "performance"  # Speed/memory issue
    USABILITY = "usability"  # Confusing UX
    INTEGRATION = "integration"  # Integration with other tools


class FeedbackPriority(Enum):
    """Priority levels for feedback."""
    CRITICAL = "critical"  # Blocks core functionality
    HIGH = "high"  # Significantly impacts workflow
    MEDIUM = "medium"  # Noticeable but has workaround
    LOW = "low"  # Nice to have
    ENHANCEMENT = "enhancement"  # New idea


@dataclass
class FeedbackItem:
    """Single feedback item."""
    
    category: FeedbackCategory
    priority: FeedbackPriority
    title: str
    description: str
    
    # Context
    timestamp: str
    cortex_version: str
    platform: str  # Windows/Mac/Linux
    
    # Technical Details
    error_message: Optional[str] = None
    stack_trace: Optional[str] = None
    operation_attempted: Optional[str] = None
    
    # User Impact
    frequency: str = "once"  # once, occasionally, frequently, always
    workaround_exists: bool = False
    
    # Privacy-Protected Context
    anonymized_path: Optional[str] = None  # Hashed file paths
    environment_hash: Optional[str] = None  # Hashed environment ID
    
    # Metadata
    auto_collected: bool = False  # True if auto-collected, False if user-submitted
    tags: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'category': self.category.value,
            'priority': self.priority.value,
            'title': self.title,
            'description': self.description,
            'timestamp': self.timestamp,
            'cortex_version': self.cortex_version,
            'platform': self.platform,
            'error_message': self.error_message,
            'stack_trace': self.stack_trace,
            'operation_attempted': self.operation_attempted,
            'frequency': self.frequency,
            'workaround_exists': self.workaround_exists,
            'anonymized_path': self.anonymized_path,
            'environment_hash': self.environment_hash,
            'auto_collected': self.auto_collected,
            'tags': self.tags,
        }


class FeedbackCollector:
    """
    Collects feedback about CORTEX usage and functionality.
    
    Features:
    - Automatic error tracking
    - Manual feedback submission
    - Privacy protection (anonymization)
    - Aggregation and reporting
    
    Usage:
        collector = FeedbackCollector()
        
        # Manual feedback
        collector.submit_feedback(
            category=FeedbackCategory.BUG,
            title="Response template not loading",
            description="When I run 'help', templates don't render"
        )
        
        # Auto-collect from error
        try:
            risky_operation()
        except Exception as e:
            collector.collect_error(e, operation="risky_operation")
    """
    
    def __init__(self, storage_path: Optional[Path] = None):
        """
        Initialize feedback collector.
        
        Args:
            storage_path: Path to store feedback (default: cortex-brain/feedback/)
        """
        self.storage_path = storage_path or Path.cwd() / "cortex-brain" / "feedback"
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        self.feedback_items: List[FeedbackItem] = []
        
        # Privacy protection patterns
        self.sensitive_patterns = [
            r'[A-Za-z]:\\Users\\[^\\]+',  # Windows user paths
            r'/Users/[^/]+',  # Mac user paths
            r'/home/[^/]+',  # Linux user paths
            r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',  # Emails
            r'password["\']?\s*[:=]\s*["\']?[^"\'\s]+',  # Passwords
            r'token["\']?\s*[:=]\s*["\']?[^"\'\s]+',  # Tokens
            r'api[_-]?key["\']?\s*[:=]\s*["\']?[^"\'\s]+',  # API keys
        ]
        
        # Load existing feedback
        self._load_feedback()
    
    def submit_feedback(
        self,
        category: FeedbackCategory,
        title: str,
        description: str,
        priority: FeedbackPriority = FeedbackPriority.MEDIUM,
        frequency: str = "once",
        workaround_exists: bool = False,
        tags: Optional[List[str]] = None,
    ) -> FeedbackItem:
        """
        Submit manual feedback.
        
        Args:
            category: Feedback category
            title: Brief title
            description: Detailed description
            priority: Priority level
            frequency: How often it occurs
            workaround_exists: Is there a workaround?
            tags: Optional tags for categorization
        
        Returns:
            Created FeedbackItem
        """
        item = FeedbackItem(
            category=category,
            priority=priority,
            title=title,
            description=self._anonymize(description),
            timestamp=datetime.now().isoformat(),
            cortex_version=self._get_cortex_version(),
            platform=platform.system(),
            frequency=frequency,
            workaround_exists=workaround_exists,
            environment_hash=self._get_environment_hash(),
            auto_collected=False,
            tags=tags or [],
        )
        
        self.feedback_items.append(item)
        self._save_feedback()
        
        logger.info(f"Feedback submitted: {title}")
        return item
    
    def collect_error(
        self,
        error: Exception,
        operation: str,
        priority: FeedbackPriority = FeedbackPriority.HIGH,
        context: Optional[Dict[str, Any]] = None,
    ) -> FeedbackItem:
        """
        Auto-collect feedback from error.
        
        Args:
            error: Exception that occurred
            operation: Operation that was attempted
            priority: Priority level
            context: Additional context
        
        Returns:
            Created FeedbackItem
        """
        import traceback
        
        # Extract error details
        error_type = type(error).__name__
        error_message = str(error)
        stack_trace = traceback.format_exc()
        
        # Anonymize
        error_message = self._anonymize(error_message)
        stack_trace = self._anonymize(stack_trace)
        
        # Create feedback item
        item = FeedbackItem(
            category=FeedbackCategory.BUG,
            priority=priority,
            title=f"{error_type} in {operation}",
            description=f"Error occurred during {operation}: {error_message}",
            timestamp=datetime.now().isoformat(),
            cortex_version=self._get_cortex_version(),
            platform=platform.system(),
            error_message=error_message,
            stack_trace=stack_trace,
            operation_attempted=operation,
            environment_hash=self._get_environment_hash(),
            auto_collected=True,
            tags=['auto-collected', 'error', operation],
        )
        
        self.feedback_items.append(item)
        self._save_feedback()
        
        logger.info(f"Error feedback collected: {error_type}")
        return item
    
    def collect_usage_pattern(
        self,
        operation: str,
        success: bool,
        duration_seconds: float,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Collect usage pattern (what works, what doesn't).
        
        Args:
            operation: Operation performed
            success: Did it succeed?
            duration_seconds: How long it took
            metadata: Additional metadata
        """
        # Aggregate usage patterns (don't create individual items)
        patterns_file = self.storage_path / "usage_patterns.json"
        
        patterns = {}
        if patterns_file.exists():
            try:
                patterns = json.loads(patterns_file.read_text(encoding='utf-8'))
            except Exception:
                patterns = {}
        
        # Update pattern
        if operation not in patterns:
            patterns[operation] = {
                'total_uses': 0,
                'successes': 0,
                'failures': 0,
                'avg_duration_seconds': 0.0,
                'last_used': None,
            }
        
        patterns[operation]['total_uses'] += 1
        if success:
            patterns[operation]['successes'] += 1
        else:
            patterns[operation]['failures'] += 1
        
        # Update average duration
        total = patterns[operation]['total_uses']
        old_avg = patterns[operation]['avg_duration_seconds']
        patterns[operation]['avg_duration_seconds'] = (
            (old_avg * (total - 1) + duration_seconds) / total
        )
        patterns[operation]['last_used'] = datetime.now().isoformat()
        
        # Save
        patterns_file.write_text(
            json.dumps(patterns, indent=2),
            encoding='utf-8'
        )
    
    def get_all_feedback(self) -> List[FeedbackItem]:
        """Get all collected feedback."""
        return self.feedback_items.copy()
    
    def get_feedback_by_category(
        self,
        category: FeedbackCategory
    ) -> List[FeedbackItem]:
        """Get feedback filtered by category."""
        return [
            item for item in self.feedback_items
            if item.category == category
        ]
    
    def get_feedback_by_priority(
        self,
        priority: FeedbackPriority
    ) -> List[FeedbackItem]:
        """Get feedback filtered by priority."""
        return [
            item for item in self.feedback_items
            if item.priority == priority
        ]
    
    def get_usage_patterns(self) -> Dict[str, Any]:
        """Get aggregated usage patterns."""
        patterns_file = self.storage_path / "usage_patterns.json"
        
        if not patterns_file.exists():
            return {}
        
        try:
            return json.loads(patterns_file.read_text(encoding='utf-8'))
        except Exception:
            return {}
    
    def clear_feedback(self) -> None:
        """Clear all collected feedback (after upload to GitHub)."""
        self.feedback_items = []
        self._save_feedback()
        
        # Clear usage patterns
        patterns_file = self.storage_path / "usage_patterns.json"
        if patterns_file.exists():
            patterns_file.unlink()
    
    def _anonymize(self, text: str) -> str:
        """
        Anonymize sensitive information in text.
        
        Args:
            text: Text to anonymize
        
        Returns:
            Anonymized text
        """
        anonymized = text
        
        for pattern in self.sensitive_patterns:
            anonymized = re.sub(pattern, '[REDACTED]', anonymized)
        
        return anonymized
    
    def _get_environment_hash(self) -> str:
        """
        Get anonymized environment identifier.
        
        Returns:
            Hash of machine ID (not reversible)
        """
        # Create hash from platform info (not user-specific)
        env_string = f"{platform.system()}_{platform.release()}_{platform.machine()}"
        return hashlib.sha256(env_string.encode()).hexdigest()[:16]
    
    def _get_cortex_version(self) -> str:
        """Get CORTEX version."""
        # Try to read from version file
        version_file = Path.cwd() / "VERSION"
        if version_file.exists():
            return version_file.read_text(encoding='utf-8').strip()
        
        return "unknown"
    
    def _load_feedback(self) -> None:
        """Load existing feedback from storage."""
        feedback_file = self.storage_path / "feedback.json"
        
        if not feedback_file.exists():
            return
        
        try:
            data = json.loads(feedback_file.read_text(encoding='utf-8'))
            
            for item_data in data.get('items', []):
                item = FeedbackItem(
                    category=FeedbackCategory(item_data['category']),
                    priority=FeedbackPriority(item_data['priority']),
                    title=item_data['title'],
                    description=item_data['description'],
                    timestamp=item_data['timestamp'],
                    cortex_version=item_data['cortex_version'],
                    platform=item_data['platform'],
                    error_message=item_data.get('error_message'),
                    stack_trace=item_data.get('stack_trace'),
                    operation_attempted=item_data.get('operation_attempted'),
                    frequency=item_data.get('frequency', 'once'),
                    workaround_exists=item_data.get('workaround_exists', False),
                    anonymized_path=item_data.get('anonymized_path'),
                    environment_hash=item_data.get('environment_hash'),
                    auto_collected=item_data.get('auto_collected', False),
                    tags=item_data.get('tags', []),
                )
                self.feedback_items.append(item)
        
        except Exception as e:
            logger.warning(f"Failed to load feedback: {e}")
    
    def _save_feedback(self) -> None:
        """Save feedback to storage."""
        feedback_file = self.storage_path / "feedback.json"
        
        data = {
            'version': '1.0',
            'last_updated': datetime.now().isoformat(),
            'items': [item.to_dict() for item in self.feedback_items],
        }
        
        try:
            feedback_file.write_text(
                json.dumps(data, indent=2),
                encoding='utf-8'
            )
        except Exception as e:
            logger.error(f"Failed to save feedback: {e}")
