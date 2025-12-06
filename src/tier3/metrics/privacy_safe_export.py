"""
Privacy-Safe Export

Exports adoption analytics data with privacy protection and anonymization.
Supports JSON/CSV export with configurable anonymization levels and GitHub Gist upload.

Author: Asif Hussain
Version: 1.0.0
"""

from dataclasses import dataclass, asdict
from datetime import date
from typing import Dict, Any, List, Optional
import json
import csv
import sqlite3
from pathlib import Path
from enum import Enum
import re
import hashlib


class ExportFormat(Enum):
    """Supported export formats"""
    JSON = "json"
    CSV = "csv"


class AnonymizationLevel(Enum):
    """Anonymization levels for export"""
    NONE = "none"  # No anonymization (internal use only)
    BASIC = "basic"  # Hash engineer emails, keep team IDs
    FULL = "full"  # Hash everything, aggregate only


@dataclass
class ExportConfig:
    """Configuration for privacy-safe export"""
    format: ExportFormat = ExportFormat.JSON
    anonymization_level: AnonymizationLevel = AnonymizationLevel.FULL
    include_team_data: bool = True
    include_engineer_data: bool = False  # Only if anonymization_level != FULL
    include_roi_metrics: bool = True
    include_trends: bool = True
    aggregate_small_teams: bool = True  # Teams < 3 members aggregated
    min_team_size: int = 3


@dataclass
class ExportResult:
    """Result of export operation"""
    success: bool
    format: str
    output_path: Optional[str] = None
    gist_url: Optional[str] = None
    record_count: int = 0
    anonymization_applied: bool = False
    error_message: Optional[str] = None


class PrivacySafeExporter:
    """
    Export adoption analytics with privacy protection.
    
    Features:
    - JSON/CSV export with configurable formatting
    - Multi-level anonymization (none/basic/full)
    - PII detection and removal
    - Small team aggregation (k-anonymity)
    - GitHub Gist upload integration
    - Export validation and sanitization
    - Configurable inclusion filters
    
    Usage:
        config = ExportConfig(
            format=ExportFormat.JSON,
            anonymization_level=AnonymizationLevel.FULL,
            include_team_data=True
        )
        
        exporter = PrivacySafeExporter(db_path="/path/to/db", config=config)
        
        # Export to file
        result = exporter.export_to_file(
            output_path="/path/to/export.json",
            start_date=date(2025, 11, 1),
            end_date=date(2025, 11, 30)
        )
        
        # Export to GitHub Gist
        result = exporter.export_to_gist(
            title="Team Adoption Metrics - November 2025",
            description="Monthly adoption analytics",
            github_token="ghp_...",
            start_date=date(2025, 11, 1),
            end_date=date(2025, 11, 30)
        )
    """
    
    def __init__(self, db_path: str, config: Optional[ExportConfig] = None):
        """
        Initialize privacy-safe exporter.
        
        Args:
            db_path: Path to Tier 3 development_context.db
            config: ExportConfig with export parameters (optional)
        """
        self.db_path = Path(db_path)
        self.config = config or ExportConfig()
    
    def export_to_file(
        self,
        output_path: str,
        start_date: date,
        end_date: date
    ) -> ExportResult:
        """
        Export data to file with privacy protection.
        
        Args:
            output_path: Path for output file
            start_date: Start of export period
            end_date: End of export period
            
        Returns:
            ExportResult with export status
        """
        try:
            # Collect data
            data = self._collect_export_data(start_date, end_date)
            
            # Apply anonymization
            if self.config.anonymization_level != AnonymizationLevel.NONE:
                data = self._anonymize_data(data)
            
            # Validate no PII leakage
            validation_errors = self._validate_export(data)
            if validation_errors:
                return ExportResult(
                    success=False,
                    format=self.config.format.value,
                    error_message=f"Validation failed: {', '.join(validation_errors)}"
                )
            
            # Write to file
            output_path_obj = Path(output_path)
            if self.config.format == ExportFormat.JSON:
                self._write_json(data, output_path_obj)
            else:
                self._write_csv(data, output_path_obj)
            
            return ExportResult(
                success=True,
                format=self.config.format.value,
                output_path=str(output_path_obj),
                record_count=len(data.get('team_metrics', [])) + len(data.get('engineer_metrics', [])),
                anonymization_applied=self.config.anonymization_level != AnonymizationLevel.NONE
            )
            
        except Exception as e:
            return ExportResult(
                success=False,
                format=self.config.format.value,
                error_message=str(e)
            )
    
    def export_to_gist(
        self,
        title: str,
        description: str,
        github_token: str,
        start_date: date,
        end_date: date,
        public: bool = False
    ) -> ExportResult:
        """
        Export data to GitHub Gist with privacy protection.
        
        Args:
            title: Gist title
            description: Gist description
            github_token: GitHub personal access token
            start_date: Start of export period
            end_date: End of export period
            public: Whether gist should be public (default: False)
            
        Returns:
            ExportResult with Gist URL
        """
        try:
            # Collect and anonymize data
            data = self._collect_export_data(start_date, end_date)
            
            if self.config.anonymization_level != AnonymizationLevel.NONE:
                data = self._anonymize_data(data)
            
            # Validate
            validation_errors = self._validate_export(data)
            if validation_errors:
                return ExportResult(
                    success=False,
                    format=self.config.format.value,
                    error_message=f"Validation failed: {', '.join(validation_errors)}"
                )
            
            # Format as JSON string
            json_content = json.dumps(data, indent=2, default=str)
            
            # Upload to Gist
            gist_url = self._upload_to_gist(
                title=title,
                description=description,
                content=json_content,
                github_token=github_token,
                public=public
            )
            
            return ExportResult(
                success=True,
                format="json",
                gist_url=gist_url,
                record_count=len(data.get('team_metrics', [])) + len(data.get('engineer_metrics', [])),
                anonymization_applied=True
            )
            
        except Exception as e:
            return ExportResult(
                success=False,
                format="json",
                error_message=str(e)
            )
    
    def _collect_export_data(
        self,
        start_date: date,
        end_date: date
    ) -> Dict[str, Any]:
        """Collect all export data from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        data = {
            'export_metadata': {
                'export_date': date.today().isoformat(),
                'period_start': start_date.isoformat(),
                'period_end': end_date.isoformat(),
                'anonymization_level': self.config.anonymization_level.value
            }
        }
        
        # Team data
        if self.config.include_team_data:
            cursor.execute("""
                SELECT 
                    team_id,
                    aggregation_date,
                    team_size,
                    copilot_total_suggestions,
                    copilot_acceptance_rate,
                    cortex_total_requests,
                    cortex_success_rate
                FROM team_aggregations
                WHERE aggregation_date BETWEEN ? AND ?
                ORDER BY team_id, aggregation_date
            """, (start_date.isoformat(), end_date.isoformat()))
            
            team_metrics = []
            for row in cursor.fetchall():
                # Skip small teams if configured
                if self.config.aggregate_small_teams and row[2] < self.config.min_team_size:
                    continue
                
                team_metrics.append({
                    'team_id': row[0],
                    'date': row[1],
                    'team_size': row[2],
                    'copilot_suggestions': row[3],
                    'copilot_acceptance_rate': round(row[4], 3) if row[4] else 0.0,
                    'cortex_requests': row[5],
                    'cortex_success_rate': round(row[6], 3) if row[6] else 0.0
                })
            
            data['team_metrics'] = team_metrics
        
        # Engineer data (only if allowed)
        if self.config.include_engineer_data and self.config.anonymization_level != AnonymizationLevel.FULL:
            cursor.execute("""
                SELECT 
                    cm.engineer_hash,
                    cm.metric_date,
                    cm.total_suggestions,
                    cm.acceptances,
                    cum.total_count,
                    cum.successful_count
                FROM copilot_metrics cm
                LEFT JOIN cortex_usage_metrics cum 
                  ON cm.engineer_hash = cum.engineer_hash 
                  AND cm.metric_date = cum.metric_date
                WHERE cm.metric_date BETWEEN ? AND ?
                ORDER BY cm.engineer_hash, cm.metric_date
            """, (start_date.isoformat(), end_date.isoformat()))
            
            engineer_metrics = []
            for row in cursor.fetchall():
                engineer_metrics.append({
                    'engineer_id': row[0],
                    'date': row[1],
                    'copilot_suggestions': row[2],
                    'copilot_acceptances': row[3],
                    'cortex_requests': row[4] or 0,
                    'cortex_successes': row[5] or 0
                })
            
            data['engineer_metrics'] = engineer_metrics
        
        conn.close()
        return data
    
    def _anonymize_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply anonymization based on configuration"""
        if self.config.anonymization_level == AnonymizationLevel.NONE:
            return data
        
        # BASIC: Hash engineer IDs, keep team IDs
        if self.config.anonymization_level == AnonymizationLevel.BASIC:
            if 'engineer_metrics' in data:
                for metric in data['engineer_metrics']:
                    metric['engineer_id'] = self._hash_value(metric['engineer_id'])
        
        # FULL: Hash everything, remove granular data
        elif self.config.anonymization_level == AnonymizationLevel.FULL:
            if 'team_metrics' in data:
                for metric in data['team_metrics']:
                    metric['team_id'] = self._hash_value(metric['team_id'])
            
            # Remove engineer-level data
            if 'engineer_metrics' in data:
                del data['engineer_metrics']
        
        return data
    
    def _validate_export(self, data: Dict[str, Any]) -> List[str]:
        """Validate export for PII leakage"""
        errors = []
        
        # Convert to JSON string for pattern matching
        data_str = json.dumps(data)
        
        # Check for email patterns
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        if re.search(email_pattern, data_str):
            errors.append("Email addresses detected in export")
        
        # Check for common PII patterns
        if re.search(r'\b\d{3}-\d{2}-\d{4}\b', data_str):
            errors.append("SSN pattern detected")
        
        # Check for overly specific identifiers (less than configured minimum)
        if self.config.aggregate_small_teams and 'team_metrics' in data:
            for metric in data['team_metrics']:
                if metric.get('team_size', 0) < self.config.min_team_size:
                    errors.append(f"Team size {metric['team_size']} below minimum {self.config.min_team_size}")
        
        return errors
    
    def _write_json(self, data: Dict[str, Any], output_path: Path):
        """Write data as JSON"""
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    def _write_csv(self, data: Dict[str, Any], output_path: Path):
        """Write data as CSV"""
        with open(output_path, 'w', newline='') as f:
            if 'team_metrics' in data and data['team_metrics']:
                writer = csv.DictWriter(f, fieldnames=data['team_metrics'][0].keys())
                writer.writeheader()
                writer.writerows(data['team_metrics'])
    
    def _upload_to_gist(
        self,
        title: str,
        description: str,
        content: str,
        github_token: str,
        public: bool
    ) -> str:
        """Upload content to GitHub Gist"""
        import requests
        
        headers = {
            'Authorization': f'token {github_token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        payload = {
            'description': description,
            'public': public,
            'files': {
                f'{title}.json': {
                    'content': content
                }
            }
        }
        
        response = requests.post(
            'https://api.github.com/gists',
            headers=headers,
            json=payload
        )
        
        if response.status_code == 201:
            return response.json()['html_url']
        else:
            raise Exception(f"Gist upload failed: {response.status_code} {response.text}")
    
    def _hash_value(self, value: str) -> str:
        """Hash a value for anonymization"""
        return hashlib.sha256(value.encode()).hexdigest()[:16]
