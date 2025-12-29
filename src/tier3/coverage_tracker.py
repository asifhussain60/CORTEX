"""
CORTEX Tier 3: Test Coverage Tracker

Integrates pytest coverage collection with Tier 3 metrics storage.
Automatically captures coverage data during test runs and stores in tier3_test_activity table.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import subprocess
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, Any, List
import uuid
import sqlite3


class CoverageTracker:
    """
    Tracks test coverage for CORTEX and user applications.
    
    Integrates with pytest to capture coverage metrics and store in Tier 3.
    """
    
    def __init__(self, db_path: Path):
        """
        Initialize coverage tracker.
        
        Args:
            db_path: Path to Tier 3 development_context.db
        """
        self.db_path = Path(db_path)
    
    def run_tests_with_coverage(
        self,
        test_path: str,
        project_root: Path,
        test_suite: str = "default",
        additional_args: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Run pytest with coverage and capture results.
        
        Args:
            test_path: Path to test file/directory
            project_root: Root directory of project
            test_suite: Name of test suite (for grouping)
            additional_args: Optional additional pytest arguments
            
        Returns:
            Dict with success, coverage_percentage, test metrics
        """
        project_root = Path(project_root)
        coverage_dir = project_root / ".coverage_temp"
        coverage_dir.mkdir(exist_ok=True)
        
        try:
            # Build pytest command with coverage
            cmd = [
                "pytest",
                str(test_path),
                f"--cov={project_root}",
                f"--cov-report=xml:{coverage_dir}/coverage.xml",
                f"--cov-report=json:{coverage_dir}/coverage.json",
                "--cov-report=term",
                "-v",
                "--tb=short"
            ]
            
            if additional_args:
                cmd.extend(additional_args)
            
            # Run pytest
            result = subprocess.run(
                cmd,
                cwd=project_root,
                capture_output=True,
                text=True
            )
            
            # Parse coverage from XML (most reliable)
            coverage_percentage = self._parse_coverage_xml(coverage_dir / "coverage.xml")
            
            # Parse test results from output
            test_metrics = self._parse_pytest_output(result.stdout)
            
            # Store in Tier 3
            test_run_id = self._store_coverage_data(
                test_suite=test_suite,
                coverage_percentage=coverage_percentage,
                test_metrics=test_metrics,
                duration_seconds=test_metrics.get("duration_seconds", 0.0)
            )
            
            return {
                "success": result.returncode == 0,
                "test_run_id": test_run_id,
                "coverage_percentage": coverage_percentage,
                "total_tests": test_metrics.get("total", 0),
                "passed_tests": test_metrics.get("passed", 0),
                "failed_tests": test_metrics.get("failed", 0),
                "skipped_tests": test_metrics.get("skipped", 0),
                "duration_seconds": test_metrics.get("duration_seconds", 0.0),
                "output": result.stdout,
                "errors": result.stderr if result.returncode != 0 else None
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "test_run_id": None
            }
    
    def _parse_coverage_xml(self, xml_path: Path) -> Optional[float]:
        """
        Parse coverage percentage from XML report.
        
        Args:
            xml_path: Path to coverage.xml
            
        Returns:
            Coverage percentage (0-100) or None if parsing fails
        """
        try:
            if not xml_path.exists():
                return None
            
            tree = ET.parse(xml_path)
            root = tree.getroot()
            
            # Coverage XML format: <coverage line-rate="0.85" ...>
            # line-rate is 0-1, convert to 0-100
            line_rate = float(root.attrib.get("line-rate", 0))
            return round(line_rate * 100, 2)
        
        except Exception:
            return None
    
    def _parse_coverage_json(self, json_path: Path) -> Optional[float]:
        """
        Parse coverage percentage from JSON report (fallback).
        
        Args:
            json_path: Path to coverage.json
            
        Returns:
            Coverage percentage (0-100) or None if parsing fails
        """
        try:
            if not json_path.exists():
                return None
            
            with open(json_path, 'r') as f:
                data = json.load(f)
            
            # Coverage JSON format: {"totals": {"percent_covered": 85.5}}
            return round(data.get("totals", {}).get("percent_covered", 0), 2)
        
        except Exception:
            return None
    
    def _parse_pytest_output(self, output: str) -> Dict[str, Any]:
        """
        Parse pytest output for test counts and duration.
        
        Args:
            output: pytest stdout
            
        Returns:
            Dict with total, passed, failed, skipped, duration_seconds
        """
        metrics = {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "duration_seconds": 0.0
        }
        
        try:
            # Parse test results line (e.g., "5 passed, 2 failed in 3.45s")
            for line in output.split('\n'):
                if 'passed' in line or 'failed' in line or 'skipped' in line:
                    # Extract counts
                    if 'passed' in line:
                        parts = line.split('passed')
                        if parts:
                            try:
                                metrics['passed'] = int(parts[0].strip().split()[-1])
                            except (ValueError, IndexError):
                                pass
                    
                    if 'failed' in line:
                        parts = line.split('failed')
                        if parts and len(parts[0].split()) > 0:
                            try:
                                # Handle "5 passed, 2 failed" format
                                failed_part = parts[0].strip().split(',')[-1].strip()
                                metrics['failed'] = int(failed_part.split()[0])
                            except (ValueError, IndexError):
                                pass
                    
                    if 'skipped' in line:
                        parts = line.split('skipped')
                        if parts and len(parts[0].split()) > 0:
                            try:
                                skipped_part = parts[0].strip().split(',')[-1].strip()
                                metrics['skipped'] = int(skipped_part.split()[0])
                            except (ValueError, IndexError):
                                pass
                    
                    # Extract duration (e.g., "in 3.45s")
                    if ' in ' in line:
                        duration_part = line.split(' in ')[-1]
                        try:
                            duration_str = duration_part.split('s')[0].strip()
                            metrics['duration_seconds'] = float(duration_str)
                        except (ValueError, IndexError):
                            pass
            
            # Calculate total
            metrics['total'] = metrics['passed'] + metrics['failed'] + metrics['skipped']
        
        except Exception:
            pass
        
        return metrics
    
    def _store_coverage_data(
        self,
        test_suite: str,
        coverage_percentage: Optional[float],
        test_metrics: Dict[str, Any],
        duration_seconds: float
    ) -> str:
        """
        Store coverage data in Tier 3 database.
        
        Args:
            test_suite: Name of test suite
            coverage_percentage: Coverage percentage (0-100)
            test_metrics: Dict with test counts
            duration_seconds: Test execution duration
            
        Returns:
            test_run_id
        """
        test_run_id = f"run-{uuid.uuid4().hex[:12]}"
        timestamp = datetime.now().isoformat()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO tier3_test_activity (
                test_run_id,
                timestamp,
                test_suite,
                total_tests,
                passed_tests,
                failed_tests,
                skipped_tests,
                duration_seconds,
                coverage_percentage
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            test_run_id,
            timestamp,
            test_suite,
            test_metrics.get("total", 0),
            test_metrics.get("passed", 0),
            test_metrics.get("failed", 0),
            test_metrics.get("skipped", 0),
            duration_seconds,
            coverage_percentage
        ))
        
        conn.commit()
        conn.close()
        
        return test_run_id
    
    def get_coverage_trends(
        self,
        test_suite: Optional[str] = None,
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Get coverage trends over time.
        
        Args:
            test_suite: Optional test suite filter
            days: Number of days to look back
            
        Returns:
            List of coverage data points
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if test_suite:
            cursor.execute("""
                SELECT 
                    test_run_id,
                    timestamp,
                    test_suite,
                    coverage_percentage,
                    total_tests,
                    passed_tests
                FROM tier3_test_activity
                WHERE test_suite = ?
                    AND timestamp >= datetime('now', ?)
                    AND coverage_percentage IS NOT NULL
                ORDER BY timestamp DESC
            """, (test_suite, f'-{days} days'))
        else:
            cursor.execute("""
                SELECT 
                    test_run_id,
                    timestamp,
                    test_suite,
                    coverage_percentage,
                    total_tests,
                    passed_tests
                FROM tier3_test_activity
                WHERE timestamp >= datetime('now', ?)
                    AND coverage_percentage IS NOT NULL
                ORDER BY timestamp DESC
            """, (f'-{days} days',))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                "test_run_id": row[0],
                "timestamp": row[1],
                "test_suite": row[2],
                "coverage_percentage": row[3],
                "total_tests": row[4],
                "passed_tests": row[5]
            })
        
        conn.close()
        return results
    
    def get_latest_coverage(self, test_suite: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Get latest coverage data.
        
        Args:
            test_suite: Optional test suite filter
            
        Returns:
            Latest coverage data or None
        """
        trends = self.get_coverage_trends(test_suite=test_suite, days=1)
        return trends[0] if trends else None
