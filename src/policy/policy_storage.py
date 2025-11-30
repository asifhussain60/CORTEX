"""
Policy Storage - Tier 3 Per-Repo Policy Management

Purpose: Store and track policy documents per repository with change detection.
         Enables historical tracking and automatic re-validation on policy updates.

Features:
- Per-repository policy storage in cortex-brain/tier3/policies/
- SHA256 hash tracking for change detection
- SQLite database for policy metadata and validation history
- Compliance report archival with timestamps
- Automatic re-validation triggers on policy changes

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
Repository: https://github.com/asifhussain60/CORTEX
"""

import os
import sqlite3
import json
import hashlib
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from dataclasses import asdict

try:
    from .policy_analyzer import PolicyAnalyzer, PolicyDocument
    from .compliance_validator import ComplianceValidator, ComplianceReport
except ImportError:
    # For standalone execution
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from src.policy.policy_analyzer import PolicyAnalyzer, PolicyDocument
    from src.policy.compliance_validator import ComplianceValidator, ComplianceReport


class PolicyStorage:
    """
    Manage policy storage and tracking in Tier 3.
    
    Directory structure:
        cortex-brain/tier3/policies/
        ├── {repo_name}/
        │   ├── policies/
        │   │   ├── security-policy.md
        │   │   ├── security-policy.md.sha256
        │   │   └── quality-policy.pdf
        │   ├── reports/
        │   │   ├── security-policy-2025-11-26-180000.json
        │   │   └── quality-policy-2025-11-26-180000.json
        │   ├── metadata.db (SQLite: versions, timestamps, scores)
        │   └── latest-report.json (most recent validation)
    """
    
    def __init__(self, brain_path: str = None):
        """
        Initialize policy storage.
        
        Args:
            brain_path: Path to cortex-brain directory. If None, auto-detect.
        """
        if brain_path is None:
            # Auto-detect brain path
            current_file = Path(__file__).resolve()
            cortex_root = current_file.parent.parent.parent
            brain_path = cortex_root / "cortex-brain"
        
        self.brain_path = Path(brain_path)
        self.tier3_path = self.brain_path / "tier3" / "policies"
        self.tier3_path.mkdir(parents=True, exist_ok=True)
        
        self.analyzer = PolicyAnalyzer()
        self.validator = ComplianceValidator()
    
    def get_repo_path(self, repo_name: str) -> Path:
        """Get path for a specific repository's policies"""
        repo_path = self.tier3_path / repo_name
        repo_path.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        (repo_path / "policies").mkdir(exist_ok=True)
        (repo_path / "reports").mkdir(exist_ok=True)
        
        return repo_path
    
    def get_db_connection(self, repo_name: str) -> sqlite3.Connection:
        """Get SQLite connection for repo metadata"""
        repo_path = self.get_repo_path(repo_name)
        db_path = repo_path / "metadata.db"
        
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        
        # Create tables if not exist
        self._init_db_schema(conn)
        
        return conn
    
    def _init_db_schema(self, conn: sqlite3.Connection):
        """Initialize database schema"""
        conn.executescript('''
            CREATE TABLE IF NOT EXISTS policies (
                policy_id TEXT PRIMARY KEY,
                policy_name TEXT NOT NULL,
                file_path TEXT NOT NULL,
                file_hash TEXT NOT NULL,
                title TEXT,
                version TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                rules_count INTEGER DEFAULT 0
            );
            
            CREATE TABLE IF NOT EXISTS validations (
                validation_id INTEGER PRIMARY KEY AUTOINCREMENT,
                policy_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                codebase_path TEXT NOT NULL,
                compliance_score REAL NOT NULL,
                violations_count INTEGER DEFAULT 0,
                critical_violations INTEGER DEFAULT 0,
                high_violations INTEGER DEFAULT 0,
                medium_violations INTEGER DEFAULT 0,
                low_violations INTEGER DEFAULT 0,
                report_path TEXT,
                FOREIGN KEY (policy_id) REFERENCES policies(policy_id)
            );
            
            CREATE INDEX IF NOT EXISTS idx_validations_policy 
            ON validations(policy_id);
            
            CREATE INDEX IF NOT EXISTS idx_validations_timestamp 
            ON validations(timestamp);
        ''')
        conn.commit()
    
    def store_policy(
        self,
        repo_name: str,
        policy_file: str,
        policy_name: str = None
    ) -> Tuple[str, bool]:
        """
        Store a policy document in Tier 3.
        
        Args:
            repo_name: Repository identifier
            policy_file: Path to policy document
            policy_name: Optional name (defaults to filename)
        
        Returns:
            Tuple of (policy_id, changed)
            - policy_id: Unique identifier for the policy
            - changed: True if policy changed from previous version
        """
        policy_file = Path(policy_file)
        
        if not policy_file.exists():
            raise FileNotFoundError(f"Policy file not found: {policy_file}")
        
        # Parse policy
        policy_doc = self.analyzer.analyze_file(str(policy_file))
        
        # Generate policy ID
        if policy_name is None:
            policy_name = policy_file.stem
        
        policy_id = f"{repo_name}-{policy_name}".replace(" ", "-").lower()
        
        # Calculate hash
        with open(policy_file, 'rb') as f:
            file_hash = hashlib.sha256(f.read()).hexdigest()
        
        # Get storage paths
        repo_path = self.get_repo_path(repo_name)
        stored_policy = repo_path / "policies" / policy_file.name
        stored_hash = repo_path / "policies" / f"{policy_file.name}.sha256"
        
        # Check if changed
        changed = True
        if stored_hash.exists():
            with open(stored_hash, 'r') as f:
                old_hash = f.read().strip()
                changed = (old_hash != file_hash)
        
        # Copy policy file
        import shutil
        shutil.copy2(policy_file, stored_policy)
        
        # Write hash
        with open(stored_hash, 'w') as f:
            f.write(file_hash)
        
        # Update database
        conn = self.get_db_connection(repo_name)
        cursor = conn.cursor()
        
        now = datetime.now().isoformat()
        
        cursor.execute('''
            INSERT OR REPLACE INTO policies (
                policy_id, policy_name, file_path, file_hash,
                title, version, created_at, updated_at, rules_count
            ) VALUES (?, ?, ?, ?, ?, ?, 
                COALESCE((SELECT created_at FROM policies WHERE policy_id = ?), ?),
                ?, ?)
        ''', (
            policy_id,
            policy_name,
            str(stored_policy),
            file_hash,
            policy_doc.title,
            policy_doc.version,
            policy_id,
            now,
            now,
            len(policy_doc.rules)
        ))
        
        conn.commit()
        conn.close()
        
        print(f"{'✅ Updated' if changed else '✓ Stored'} policy: {policy_name}")
        print(f"   ID: {policy_id}")
        print(f"   Rules: {len(policy_doc.rules)}")
        print(f"   Hash: {file_hash[:16]}...")
        
        return policy_id, changed
    
    def validate_and_store(
        self,
        repo_name: str,
        policy_id: str,
        codebase_path: str
    ) -> ComplianceReport:
        """
        Validate codebase against policy and store report.
        
        Args:
            repo_name: Repository identifier
            policy_id: Policy identifier
            codebase_path: Path to codebase to validate
        
        Returns:
            ComplianceReport object
        """
        # Get policy
        conn = self.get_db_connection(repo_name)
        cursor = conn.cursor()
        
        cursor.execute('SELECT file_path FROM policies WHERE policy_id = ?', (policy_id,))
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            raise ValueError(f"Policy not found: {policy_id}")
        
        policy_file = row['file_path']
        
        # Parse and validate
        policy_doc = self.analyzer.analyze_file(policy_file)
        report = self.validator.validate(policy_doc, codebase_path)
        
        # Store report
        repo_path = self.get_repo_path(repo_name)
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        report_file = repo_path / "reports" / f"{policy_id}-{timestamp}.json"
        
        # Convert report to dict
        report_dict = self._report_to_dict(report)
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_dict, f, indent=2)
        
        # Also save as latest
        latest_file = repo_path / "latest-report.json"
        with open(latest_file, 'w', encoding='utf-8') as f:
            json.dump(report_dict, f, indent=2)
        
        # Update database
        cursor.execute('''
            INSERT INTO validations (
                policy_id, timestamp, codebase_path, compliance_score,
                violations_count, critical_violations, high_violations,
                medium_violations, low_violations, report_path
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            policy_id,
            datetime.now().isoformat(),
            codebase_path,
            report.compliance_score,
            len(report.violations),
            len([v for v in report.violations if v.severity == "critical"]),
            len([v for v in report.violations if v.severity == "high"]),
            len([v for v in report.violations if v.severity == "medium"]),
            len([v for v in report.violations if v.severity == "low"]),
            str(report_file)
        ))
        
        conn.commit()
        conn.close()
        
        print(f"\n✅ Validation Complete")
        print(f"   Score: {report.compliance_score}%")
        print(f"   Violations: {len(report.violations)}")
        print(f"   Report: {report_file}")
        
        return report
    
    def _report_to_dict(self, report: ComplianceReport) -> Dict[str, Any]:
        """Convert ComplianceReport to dictionary"""
        
        def convert_item(item):
            """Convert dataclass to dict, handling datetime objects"""
            if hasattr(item, '__dict__'):
                result = {}
                for key, value in asdict(item).items():
                    if isinstance(value, datetime):
                        result[key] = value.isoformat()
                    elif isinstance(value, list):
                        result[key] = [convert_item(v) for v in value]
                    elif isinstance(value, dict):
                        result[key] = {k: convert_item(v) for k, v in value.items()}
                    else:
                        result[key] = value
                return result
            return item
        
        return {
            'timestamp': report.timestamp if isinstance(report.timestamp, str) else report.timestamp.isoformat(),
            'compliance_score': report.compliance_score,
            'violations': [convert_item(v) for v in report.violations],
            'gap_analyses': [convert_item(g) for g in report.gap_analyses],
            'remediation_actions': [convert_item(r) for r in report.remediation_actions],
            'summary': report.summary
        }
    
    def check_for_changes(self, repo_name: str) -> List[Tuple[str, str]]:
        """
        Check for policy changes that require re-validation.
        
        Args:
            repo_name: Repository identifier
        
        Returns:
            List of (policy_id, policy_name) tuples for changed policies
        """
        conn = self.get_db_connection(repo_name)
        cursor = conn.cursor()
        
        cursor.execute('SELECT policy_id, policy_name, file_path, file_hash FROM policies')
        policies = cursor.fetchall()
        
        conn.close()
        
        changed = []
        
        for policy in policies:
            policy_file = Path(policy['file_path'])
            
            if not policy_file.exists():
                continue
            
            # Calculate current hash
            with open(policy_file, 'rb') as f:
                current_hash = hashlib.sha256(f.read()).hexdigest()
            
            # Compare with stored hash
            if current_hash != policy['file_hash']:
                changed.append((policy['policy_id'], policy['policy_name']))
                print(f"⚠️  Policy changed: {policy['policy_name']}")
        
        return changed
    
    def get_validation_history(
        self,
        repo_name: str,
        policy_id: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get validation history for a policy.
        
        Args:
            repo_name: Repository identifier
            policy_id: Policy identifier
            limit: Maximum number of records to return
        
        Returns:
            List of validation records
        """
        conn = self.get_db_connection(repo_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM validations
            WHERE policy_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (policy_id, limit))
        
        records = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        return records
    
    def get_latest_report(self, repo_name: str) -> Optional[Dict[str, Any]]:
        """Get the most recent validation report"""
        repo_path = self.get_repo_path(repo_name)
        latest_file = repo_path / "latest-report.json"
        
        if not latest_file.exists():
            return None
        
        with open(latest_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def list_policies(self, repo_name: str) -> List[Dict[str, Any]]:
        """List all policies for a repository"""
        conn = self.get_db_connection(repo_name)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM policies ORDER BY updated_at DESC')
        policies = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        return policies


def main():
    """Test policy storage"""
    import tempfile
    
    # Create sample policy
    sample_policy = """# Test Policy
Version: 1.0
Date: 2025-11-26

## Security Requirements

- Passwords MUST NOT be stored in plain text.
- API keys SHOULD NOT be hardcoded.

## Testing Requirements

- Test coverage MUST be greater than 80%.
"""
    
    # Write to temp file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write(sample_policy)
        policy_path = f.name
    
    try:
        # Test storage
        storage = PolicyStorage()
        
        print("=" * 60)
        print("Testing Policy Storage")
        print("=" * 60)
        
        # Store policy
        policy_id, changed = storage.store_policy(
            repo_name="cortex-test",
            policy_file=policy_path,
            policy_name="test-policy"
        )
        
        print(f"\n" + "=" * 60)
        
        # Validate and store report
        report = storage.validate_and_store(
            repo_name="cortex-test",
            policy_id=policy_id,
            codebase_path="."
        )
        
        print(f"\n" + "=" * 60)
        
        # Check for changes
        changes = storage.check_for_changes("cortex-test")
        if not changes:
            print("✓ No policy changes detected")
        
        print(f"\n" + "=" * 60)
        
        # Get history
        history = storage.get_validation_history("cortex-test", policy_id)
        print(f"📊 Validation History: {len(history)} record(s)")
        for i, record in enumerate(history, 1):
            print(f"   {i}. {record['timestamp'][:19]} - Score: {record['compliance_score']}%")
        
        print(f"\n" + "=" * 60)
        
        # List policies
        policies = storage.list_policies("cortex-test")
        print(f"📋 Stored Policies: {len(policies)}")
        for policy in policies:
            print(f"   • {policy['policy_name']} - {policy['rules_count']} rules")
        
        print(f"\n" + "=" * 60)
        print("✅ Policy Storage Test Complete!")
        print("=" * 60)
    
    finally:
        os.unlink(policy_path)


if __name__ == "__main__":
    main()
