"""
Feedback Aggregator - Centralized Feedback Collection
Addresses Gap #9: Feedback stays local with no review mechanism

Purpose:
- Downloads feedback from all user Gists
- Merges into central feedback-aggregate.db
- Generates trend reports (top issues, patterns)
- Provides admin dashboard data

Author: GitHub Copilot
Created: 2024-11-25
"""

import os
import json
import sqlite3
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import logging
import requests

logger = logging.getLogger(__name__)


@dataclass
class AggregatedFeedback:
    """Aggregated feedback entry."""
    
    feedback_id: str
    gist_id: str
    user_hash: str  # Anonymized user identifier
    category: str
    priority: str
    title: str
    description: str
    timestamp: str
    cortex_version: str
    platform: str
    occurrence_count: int = 1
    first_seen: Optional[str] = None
    last_seen: Optional[str] = None
    
    def __post_init__(self):
        if not self.first_seen:
            self.first_seen = self.timestamp
        if not self.last_seen:
            self.last_seen = self.timestamp


@dataclass
class FeedbackTrend:
    """Trend analysis result."""
    
    issue_signature: str
    category: str
    priority: str
    title: str
    occurrence_count: int
    unique_users: int
    first_reported: str
    last_reported: str
    platforms: List[str]
    cortex_versions: List[str]


class FeedbackAggregator:
    """
    Aggregates feedback from multiple sources into central database.
    
    Features:
    - Downloads from GitHub Gists with 'cortex-feedback' tag
    - Deduplicates similar feedback items
    - Tracks occurrence counts and trends
    - Generates top issues report
    - Privacy-preserving (hashes user identifiers)
    """
    
    def __init__(self, db_path: Optional[Path] = None, github_token: Optional[str] = None):
        """
        Initialize feedback aggregator.
        
        Args:
            db_path: Path to aggregate database (default: cortex-brain/feedback/feedback-aggregate.db)
            github_token: GitHub personal access token for API access
        """
        if db_path is None:
            cortex_root = Path(__file__).parent.parent.parent
            db_path = cortex_root / "cortex-brain" / "feedback" / "feedback-aggregate.db"
        
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.github_token = github_token or os.environ.get('GITHUB_TOKEN')
        
        # Initialize database
        self._init_database()
    
    def _init_database(self) -> None:
        """Initialize SQLite database with schema."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Feedback items table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS feedback_items (
                feedback_id TEXT PRIMARY KEY,
                gist_id TEXT NOT NULL,
                gist_url TEXT,
                user_hash TEXT NOT NULL,
                category TEXT NOT NULL,
                priority TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                timestamp TEXT NOT NULL,
                cortex_version TEXT,
                platform TEXT,
                error_message TEXT,
                stack_trace TEXT,
                operation_attempted TEXT,
                frequency TEXT,
                workaround_exists INTEGER,
                tags TEXT,
                issue_signature TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Occurrence tracking table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS feedback_occurrences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                issue_signature TEXT NOT NULL,
                feedback_id TEXT NOT NULL,
                user_hash TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                cortex_version TEXT,
                platform TEXT,
                FOREIGN KEY (feedback_id) REFERENCES feedback_items(feedback_id)
            )
        """)
        
        # Gist tracking table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS gist_tracking (
                gist_id TEXT PRIMARY KEY,
                gist_url TEXT NOT NULL,
                user_hash TEXT NOT NULL,
                last_fetched TEXT NOT NULL,
                feedback_count INTEGER DEFAULT 0
            )
        """)
        
        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_issue_signature ON feedback_items(issue_signature)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_category_priority ON feedback_items(category, priority)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON feedback_items(timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_occurrence_signature ON feedback_occurrences(issue_signature)")
        
        conn.commit()
        conn.close()
    
    def fetch_feedback_from_gists(self, username: Optional[str] = None, tag: str = "cortex-feedback") -> int:
        """
        Fetch feedback from GitHub Gists.
        
        Args:
            username: GitHub username to fetch gists from (None = all public gists)
            tag: Tag to filter gists (default: cortex-feedback)
        
        Returns:
            Number of new feedback items added
        """
        if not self.github_token:
            logger.warning("No GitHub token provided, cannot fetch gists")
            return 0
        
        headers = {
            "Authorization": f"token {self.github_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        # Fetch gists
        if username:
            url = f"https://api.github.com/users/{username}/gists"
        else:
            url = "https://api.github.com/gists/public"
        
        try:
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            gists = response.json()
        except Exception as e:
            logger.error(f"Failed to fetch gists: {e}")
            return 0
        
        new_items = 0
        
        for gist in gists:
            # Check if gist contains cortex feedback
            if not self._is_feedback_gist(gist, tag):
                continue
            
            # Check if already processed
            if self._is_gist_processed(gist['id']):
                continue
            
            # Download and process gist content
            items = self._process_gist(gist)
            new_items += items
        
        return new_items
    
    def _is_feedback_gist(self, gist: Dict[str, Any], tag: str) -> bool:
        """Check if gist contains CORTEX feedback."""
        description = gist.get('description', '').lower()
        
        # Check description
        if tag.lower() in description or 'cortex' in description:
            return True
        
        # Check filenames
        for filename in gist.get('files', {}).keys():
            if 'cortex' in filename.lower() and 'feedback' in filename.lower():
                return True
        
        return False
    
    def _is_gist_processed(self, gist_id: str) -> bool:
        """Check if gist was already processed."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT 1 FROM gist_tracking WHERE gist_id = ?", (gist_id,))
        result = cursor.fetchone()
        
        conn.close()
        return result is not None
    
    def _process_gist(self, gist: Dict[str, Any]) -> int:
        """
        Process gist content and extract feedback.
        
        Args:
            gist: Gist metadata dictionary
        
        Returns:
            Number of feedback items added
        """
        gist_id = gist['id']
        gist_url = gist['html_url']
        user_hash = self._hash_user_id(gist.get('owner', {}).get('login', 'anonymous'))
        
        items_added = 0
        
        # Process each file in gist
        for filename, file_data in gist.get('files', {}).items():
            try:
                # Download file content
                content_url = file_data.get('raw_url')
                if not content_url:
                    continue
                
                response = requests.get(content_url, timeout=30)
                response.raise_for_status()
                content = response.text
                
                # Parse feedback (JSON or Markdown)
                if filename.endswith('.json'):
                    feedback_data = json.loads(content)
                    items = self._extract_feedback_from_json(feedback_data, gist_id, gist_url, user_hash)
                else:
                    items = self._extract_feedback_from_markdown(content, gist_id, gist_url, user_hash)
                
                # Store feedback items
                for item in items:
                    if self._store_feedback_item(item):
                        items_added += 1
            
            except Exception as e:
                logger.error(f"Failed to process gist file {filename}: {e}")
        
        # Track gist
        self._track_gist(gist_id, gist_url, user_hash, items_added)
        
        return items_added
    
    def _extract_feedback_from_json(
        self,
        data: Dict[str, Any],
        gist_id: str,
        gist_url: str,
        user_hash: str
    ) -> List[AggregatedFeedback]:
        """Extract feedback from JSON format."""
        items = []
        
        # Handle FeedbackCollector format
        if 'items' in data:
            for item_data in data['items']:
                feedback = AggregatedFeedback(
                    feedback_id=f"{gist_id}_{hashlib.md5(item_data['title'].encode()).hexdigest()[:8]}",
                    gist_id=gist_id,
                    user_hash=user_hash,
                    category=item_data.get('category', 'unknown'),
                    priority=item_data.get('priority', 'medium'),
                    title=item_data.get('title', 'Untitled'),
                    description=item_data.get('description', ''),
                    timestamp=item_data.get('timestamp', datetime.now().isoformat()),
                    cortex_version=item_data.get('cortex_version', 'unknown'),
                    platform=item_data.get('platform', 'unknown')
                )
                items.append(feedback)
        
        return items
    
    def _extract_feedback_from_markdown(
        self,
        content: str,
        gist_id: str,
        gist_url: str,
        user_hash: str
    ) -> List[AggregatedFeedback]:
        """Extract feedback from Markdown format."""
        import re
        
        items = []
        
        # Extract metadata from Markdown
        title_match = re.search(r'# CORTEX Feedback Report: (.+)', content)
        type_match = re.search(r'\*\*Type:\*\* (.+)', content)
        severity_match = re.search(r'\*\*Severity:\*\* .+ (.+)', content)
        date_match = re.search(r'\*\*Date:\*\* (.+)', content)
        
        # Extract user feedback section
        feedback_match = re.search(r'## 📋 User Feedback\n\n(.+?)\n\n---', content, re.DOTALL)
        
        if title_match and feedback_match:
            title = title_match.group(1)
            description = feedback_match.group(1).strip()
            category = type_match.group(1).lower() if type_match else 'general'
            priority = severity_match.group(1).lower() if severity_match else 'medium'
            timestamp = date_match.group(1) if date_match else datetime.now().isoformat()
            
            feedback = AggregatedFeedback(
                feedback_id=f"{gist_id}_{hashlib.md5(title.encode()).hexdigest()[:8]}",
                gist_id=gist_id,
                user_hash=user_hash,
                category=category,
                priority=priority,
                title=title,
                description=description,
                timestamp=timestamp,
                cortex_version='unknown',
                platform='unknown'
            )
            items.append(feedback)
        
        return items
    
    def _store_feedback_item(self, feedback: AggregatedFeedback) -> bool:
        """
        Store feedback item in database.
        
        Args:
            feedback: AggregatedFeedback to store
        
        Returns:
            True if stored (new or updated), False if duplicate
        """
        # Generate issue signature (for deduplication)
        issue_signature = self._generate_issue_signature(feedback.title, feedback.category)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Check if exact feedback_id exists
            cursor.execute("SELECT 1 FROM feedback_items WHERE feedback_id = ?", (feedback.feedback_id,))
            if cursor.fetchone():
                return False  # Duplicate
            
            # Insert feedback item
            cursor.execute("""
                INSERT INTO feedback_items (
                    feedback_id, gist_id, user_hash, category, priority, title, description,
                    timestamp, cortex_version, platform, issue_signature
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                feedback.feedback_id, feedback.gist_id, feedback.user_hash, feedback.category,
                feedback.priority, feedback.title, feedback.description, feedback.timestamp,
                feedback.cortex_version, feedback.platform, issue_signature
            ))
            
            # Track occurrence
            cursor.execute("""
                INSERT INTO feedback_occurrences (
                    issue_signature, feedback_id, user_hash, timestamp, cortex_version, platform
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                issue_signature, feedback.feedback_id, feedback.user_hash, feedback.timestamp,
                feedback.cortex_version, feedback.platform
            ))
            
            conn.commit()
            return True
        
        except Exception as e:
            logger.error(f"Failed to store feedback: {e}")
            conn.rollback()
            return False
        
        finally:
            conn.close()
    
    def _track_gist(self, gist_id: str, gist_url: str, user_hash: str, feedback_count: int) -> None:
        """Track processed gist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO gist_tracking (gist_id, gist_url, user_hash, last_fetched, feedback_count)
            VALUES (?, ?, ?, ?, ?)
        """, (gist_id, gist_url, user_hash, datetime.now().isoformat(), feedback_count))
        
        conn.commit()
        conn.close()
    
    def _generate_issue_signature(self, title: str, category: str) -> str:
        """Generate signature for issue deduplication."""
        # Normalize title (lowercase, remove special chars, collapse whitespace)
        normalized = title.lower()
        normalized = re.sub(r'[^\w\s]', '', normalized)
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        
        # Combine with category
        signature_text = f"{category}:{normalized}"
        
        return hashlib.md5(signature_text.encode()).hexdigest()
    
    def _hash_user_id(self, user_id: str) -> str:
        """Hash user identifier for privacy."""
        return hashlib.sha256(user_id.encode()).hexdigest()[:16]
    
    def get_top_issues(self, limit: int = 10, days: int = 30) -> List[FeedbackTrend]:
        """
        Get top issues by occurrence count.
        
        Args:
            limit: Maximum number of issues to return
            days: Time window in days
        
        Returns:
            List of FeedbackTrend objects
        """
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                f.issue_signature,
                f.category,
                f.priority,
                f.title,
                COUNT(DISTINCT o.feedback_id) as occurrence_count,
                COUNT(DISTINCT o.user_hash) as unique_users,
                MIN(o.timestamp) as first_reported,
                MAX(o.timestamp) as last_reported,
                GROUP_CONCAT(DISTINCT o.platform) as platforms,
                GROUP_CONCAT(DISTINCT o.cortex_version) as versions
            FROM feedback_items f
            JOIN feedback_occurrences o ON f.issue_signature = o.issue_signature
            WHERE o.timestamp >= ?
            GROUP BY f.issue_signature
            ORDER BY occurrence_count DESC, unique_users DESC
            LIMIT ?
        """, (cutoff_date, limit))
        
        trends = []
        for row in cursor.fetchall():
            trend = FeedbackTrend(
                issue_signature=row[0],
                category=row[1],
                priority=row[2],
                title=row[3],
                occurrence_count=row[4],
                unique_users=row[5],
                first_reported=row[6],
                last_reported=row[7],
                platforms=row[8].split(',') if row[8] else [],
                cortex_versions=row[9].split(',') if row[9] else []
            )
            trends.append(trend)
        
        conn.close()
        return trends
    
    def generate_trend_report(self, output_path: Optional[Path] = None) -> str:
        """
        Generate Markdown trend report.
        
        Args:
            output_path: Optional path to save report
        
        Returns:
            Markdown report content
        """
        trends = self.get_top_issues(limit=10, days=30)
        
        report = f"""# CORTEX Feedback Trend Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Time Window:** Last 30 days  
**Total Issues:** {len(trends)}

---

## 🔥 Top 10 Issues

| Rank | Category | Priority | Title | Occurrences | Users | First | Last |
|------|----------|----------|-------|-------------|-------|-------|------|
"""
        
        for idx, trend in enumerate(trends, 1):
            priority_emoji = {'critical': '🔴', 'high': '🟠', 'medium': '🟡', 'low': '🟢'}.get(trend.priority, '⚪')
            
            report += f"| {idx} | {trend.category} | {priority_emoji} {trend.priority} | {trend.title[:50]}... | {trend.occurrence_count} | {trend.unique_users} | {trend.first_reported[:10]} | {trend.last_reported[:10]} |\n"
        
        report += f"""
---

## 📊 Category Breakdown

"""
        
        # Get category stats
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT category, COUNT(*) as count
            FROM feedback_items
            GROUP BY category
            ORDER BY count DESC
        """)
        
        for row in cursor.fetchall():
            report += f"- **{row[0]}**: {row[1]} items\n"
        
        conn.close()
        
        report += f"""
---

## 🎯 Recommended Actions

"""
        
        # Generate recommendations
        for idx, trend in enumerate(trends[:3], 1):
            report += f"""
### {idx}. {trend.title}

- **Occurrences:** {trend.occurrence_count} times
- **Affected Users:** {trend.unique_users}
- **Priority:** {trend.priority}
- **Action:** {"Create P0 issue" if trend.priority == 'critical' else "Add to backlog"}
"""
        
        report += f"""
---

**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.
"""
        
        # Save if output path provided
        if output_path:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(report, encoding='utf-8')
        
        return report


def main():
    """CLI entry point for feedback aggregation."""
    import argparse
    
    parser = argparse.ArgumentParser(description="CORTEX Feedback Aggregator")
    parser.add_argument('--fetch', action='store_true', help="Fetch feedback from Gists")
    parser.add_argument('--username', type=str, help="GitHub username to fetch from")
    parser.add_argument('--report', action='store_true', help="Generate trend report")
    parser.add_argument('--output', type=str, help="Output path for report")
    parser.add_argument('--token', type=str, help="GitHub personal access token")
    
    args = parser.parse_args()
    
    # Initialize aggregator
    token = args.token or os.environ.get('GITHUB_TOKEN')
    aggregator = FeedbackAggregator(github_token=token)
    
    # Fetch feedback
    if args.fetch:
        print("📥 Fetching feedback from Gists...")
        count = aggregator.fetch_feedback_from_gists(username=args.username)
        print(f"✅ Added {count} new feedback items")
    
    # Generate report
    if args.report:
        print("\n📊 Generating trend report...")
        output_path = Path(args.output) if args.output else None
        report = aggregator.generate_trend_report(output_path=output_path)
        
        if output_path:
            print(f"✅ Report saved to {output_path}")
        else:
            print("\n" + report)


if __name__ == "__main__":
    main()
