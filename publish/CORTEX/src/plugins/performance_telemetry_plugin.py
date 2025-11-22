"""
CORTEX Performance Telemetry Plugin

Collects comprehensive performance and business value metrics for team analytics.

Features:
- Performance: Execution times (avg, p50, p95, p99), success rates, error patterns
- Cost Savings: Token optimization, API cost avoidance, time saved
- Productivity: Commits, PRs, velocity, test coverage improvements
- Quality: Bug reduction, code review efficiency, test pass rates
- Copilot Enhancement: Context utilization, memory hits, suggestion quality
- Engineer Attribution: Name, email, machine config for multi-user comparison
- Platform Analysis: Windows vs Mac vs Linux performance differences

Business Value Metrics:
- ROI Calculator: Cost savings vs CORTEX investment
- Productivity Gains: Time saved per engineer per month
- Quality Improvements: Defect reduction, test coverage increase
- Executive Reporting: PowerPoint-ready dashboards

Use Case: Internal team analytics and executive ROI reporting

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary
"""

from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
import sqlite3
import yaml
import hashlib
import logging
import platform
import sys
import os
import subprocess
import socket

from src.plugins.base_plugin import BasePlugin, PluginMetadata, PluginCategory, PluginPriority
from src.plugins.hooks import HookPoint

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetric:
    """Individual performance measurement"""
    capability: str
    duration_ms: float
    success: bool
    error_type: Optional[str]
    timestamp: datetime
    tokens_saved: Optional[int] = 0
    context_size_tokens: Optional[int] = 0


@dataclass
class EngineerProfile:
    """Engineer identification and machine config"""
    engineer_name: str
    engineer_email: str
    machine_hostname: str
    machine_platform: str
    cpu_info: str
    ram_gb: int
    python_version: str
    cortex_version: str
    installation_date: Optional[datetime] = None


class PerformanceTelemetryPlugin(BasePlugin):
    """
    Collects CORTEX performance and business value metrics for team analytics.
    
    Tracked Metrics:
    1. Performance: Latency, success rates, error patterns, trends
    2. Cost Savings: Token optimization ($$$), API cost avoidance
    3. Productivity: Commits, PRs, velocity, code quality
    4. Copilot Enhancement: Memory hits, context utilization, suggestion quality
    5. Quality: Bug reduction, test coverage, code review efficiency
    
    Engineer Attribution:
    - Name, email, machine hostname
    - Machine specs (CPU, RAM, platform)
    - Installation date, CORTEX version
    
    Use Case: Internal team analytics and executive ROI reporting
    """
    
    def _get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            plugin_id="performance_telemetry",
            name="Performance Telemetry Collector",
            version="1.0.0",
            category=PluginCategory.UTILITIES,
            priority=PluginPriority.LOW,
            description="Collects CORTEX performance metrics for multi-user evaluation",
            author="Asif Hussain",
            dependencies=[],
            hooks=[HookPoint.ON_OPERATION_COMPLETE.value]
        )
    
    def initialize(self) -> bool:
        """Initialize telemetry database"""
        try:
            db_path = self._get_telemetry_db_path()
            db_path.parent.mkdir(parents=True, exist_ok=True)
            
            self._init_database(db_path)
            
            logger.info("Performance telemetry plugin initialized")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize performance telemetry: {e}")
            return False
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Record performance metric with token tracking.
        
        Args:
            context: Must contain:
                - capability_name: str (e.g., "test_generation")
                - duration_ms: float
                - success: bool
                - error_type: Optional[str] (if success=False)
                - tokens_saved: Optional[int] (CORTEX token optimization)
                - context_size_tokens: Optional[int] (context injected to Copilot)
        
        Returns:
            Execution result
        """
        try:
            # Check telemetry enabled
            if not self._has_user_consent():
                return {
                    "success": True,
                    "skipped": True,
                    "reason": "telemetry_not_enabled"
                }
            
            # Extract metric data
            capability = context.get("capability_name")
            duration_ms = context.get("duration_ms", 0)
            success = context.get("success", False)
            error_type = context.get("error_type", None) if not success else None
            tokens_saved = context.get("tokens_saved", 0)
            context_size_tokens = context.get("context_size_tokens", 0)
            
            if not capability:
                return {
                    "success": False,
                    "error": "capability_name required"
                }
            
            # Record metric
            self._record_metric(
                capability=capability,
                duration_ms=duration_ms,
                success=success,
                error_type=error_type,
                timestamp=datetime.now(),
                tokens_saved=tokens_saved,
                context_size_tokens=context_size_tokens
            )
            
            return {
                "success": True,
                "capability": capability,
                "recorded": True,
                "tokens_saved": tokens_saved
            }
            
        except Exception as e:
            logger.error(f"Failed to record performance metric: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def cleanup(self) -> bool:
        """Cleanup resources"""
        logger.info("Performance telemetry plugin cleanup")
        return True
    
    # ========================================================================
    # PUBLIC API - Export & Configuration
    # ========================================================================
    
    def export_performance_report(self, days: int = 30) -> Path:
        """
        Generate comprehensive business value report for executive presentation.
        
        Args:
            days: Number of days to aggregate (default 30)
        
        Returns:
            Path to export file (YAML)
        
        Raises:
            ValueError: If telemetry not enabled or engineer profile not setup
        """
        if not self._has_user_consent():
            raise ValueError(
                "Telemetry not enabled. "
                "Run: plugin.setup_engineer_profile('Name', 'email@company.com')"
            )
        
        engineer_email = self._get_engineer_email()
        if not engineer_email:
            raise ValueError("Engineer profile not setup")
        
        since = datetime.now() - timedelta(days=days)
        
        logger.info(f"Generating business value report (last {days} days)")
        
        # Get engineer profile
        engineer_profile = self._get_engineer_profile(engineer_email)
        
        # Aggregate all metrics
        performance_metrics = self._aggregate_metrics(since, engineer_email)
        productivity_metrics = self._aggregate_productivity(since, engineer_email)
        cost_savings = self._aggregate_cost_savings(since, engineer_email)
        copilot_metrics = self._aggregate_copilot_metrics(since, engineer_email)
        
        # Calculate ROI
        roi_analysis = self._calculate_roi(
            cost_savings,
            productivity_metrics,
            days
        )
        
        # Build comprehensive report
        report = {
            # ====== ENGINEER IDENTIFICATION ======
            "engineer_profile": {
                "name": engineer_profile["name"],
                "email": engineer_profile["email"],
                "machine": {
                    "hostname": engineer_profile["hostname"],
                    "platform": engineer_profile["platform"],
                    "cpu": engineer_profile["cpu"],
                    "ram_gb": engineer_profile["ram_gb"]
                },
                "cortex_version": engineer_profile["cortex_version"],
                "python_version": engineer_profile["python_version"]
            },
            
            # ====== REPORT METADATA ======
            "report_metadata": {
                "export_date": datetime.now().isoformat(),
                "collection_period_days": days,
                "collection_start": since.isoformat(),
                "total_executions": sum(
                    cap["metrics"]["total_executions"] 
                    for cap in performance_metrics
                )
            },
            
            # ====== EXECUTIVE SUMMARY ======
            "executive_summary": {
                "cost_savings_usd": round(cost_savings["total_saved_usd"], 2),
                "time_saved_hours": round(cost_savings["total_time_saved_minutes"] / 60, 1),
                "productivity_gain_percent": roi_analysis["productivity_gain_percent"],
                "commits_per_day": roi_analysis["commits_per_day"],
                "quality_score": roi_analysis["quality_score"],
                "copilot_enhancement": copilot_metrics["memory_hit_rate"],
                "roi_multiplier": roi_analysis["roi_multiplier"]
            },
            
            # ====== PERFORMANCE METRICS ======
            "performance": {
                "capabilities": performance_metrics,
                "total_capabilities_used": len(performance_metrics),
                "avg_success_rate": round(
                    sum(c["metrics"]["success_rate"] for c in performance_metrics) / len(performance_metrics), 
                    3
                ) if performance_metrics else 0
            },
            
            # ====== COST SAVINGS ======
            "cost_savings": {
                "total_tokens_saved": cost_savings["total_tokens_saved"],
                "total_api_calls_avoided": cost_savings["total_api_calls_avoided"],
                "total_cost_saved_usd": round(cost_savings["total_saved_usd"], 2),
                "total_time_saved_hours": round(cost_savings["total_time_saved_minutes"] / 60, 1),
                "daily_average_savings_usd": round(cost_savings["total_saved_usd"] / days, 2),
                "monthly_projection_usd": round((cost_savings["total_saved_usd"] / days) * 30, 2),
                "annual_projection_usd": round((cost_savings["total_saved_usd"] / days) * 365, 2)
            },
            
            # ====== PRODUCTIVITY METRICS ======
            "productivity": {
                "total_commits": productivity_metrics["total_commits"],
                "total_prs_created": productivity_metrics["total_prs"],
                "total_prs_merged": productivity_metrics["total_prs_merged"],
                "total_lines_added": productivity_metrics["total_lines_added"],
                "total_lines_deleted": productivity_metrics["total_lines_deleted"],
                "avg_test_coverage": productivity_metrics["avg_test_coverage"],
                "total_bugs_fixed": productivity_metrics["total_bugs_fixed"],
                "total_code_reviews": productivity_metrics["total_code_reviews"],
                "commits_per_day": round(productivity_metrics["total_commits"] / days, 2),
                "velocity_trend": productivity_metrics["velocity_trend"]
            },
            
            # ====== COPILOT ENHANCEMENT ======
            "copilot_enhancement": {
                "memory_hits": copilot_metrics["total_memory_hits"],
                "memory_misses": copilot_metrics["total_memory_misses"],
                "memory_hit_rate": round(copilot_metrics["memory_hit_rate"], 3),
                "context_injections": copilot_metrics["total_context_injections"],
                "avg_context_size_tokens": copilot_metrics["avg_context_tokens"],
                "suggestions_accepted": copilot_metrics["total_suggestions_accepted"],
                "suggestions_rejected": copilot_metrics["total_suggestions_rejected"],
                "acceptance_rate": round(copilot_metrics["acceptance_rate"], 3),
                "improvement_summary": (
                    f"CORTEX memory hit rate: {copilot_metrics['memory_hit_rate']:.1%}. "
                    f"Context injections reduced Copilot token usage by ~{cost_savings['total_tokens_saved']:,} tokens. "
                    f"Suggestion acceptance rate: {copilot_metrics['acceptance_rate']:.1%}."
                )
            },
            
            # ====== ROI ANALYSIS ======
            "roi_analysis": roi_analysis,
            
            # ====== EXECUTIVE TALKING POINTS ======
            "executive_talking_points": [
                f"💰 Cost Savings: ${cost_savings['total_saved_usd']:.2f} saved in {days} days (${(cost_savings['total_saved_usd']/days)*365:.2f}/year projected)",
                f"⏱️  Time Savings: {cost_savings['total_time_saved_minutes']/60:.1f} hours saved ({cost_savings['total_time_saved_minutes']/60/days:.1f} hrs/day avg)",
                f"📈 Productivity: {productivity_metrics['total_commits']} commits, {productivity_metrics['total_prs_merged']} PRs merged",
                f"✅ Quality: {productivity_metrics['avg_test_coverage']:.1f}% test coverage, {productivity_metrics['total_bugs_fixed']} bugs fixed",
                f"🚀 Copilot Enhancement: {copilot_metrics['memory_hit_rate']:.1%} memory hit rate, {copilot_metrics['acceptance_rate']:.1%} suggestion acceptance",
                f"🏆 ROI: {roi_analysis['roi_multiplier']:.1f}x return on investment"
            ]
        }
        
        # Export to reviewable location
        export_path = Path("cortex-brain/exports/business-value-report.yaml")
        export_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(export_path, 'w') as f:
            yaml.safe_dump(report, f, sort_keys=False, default_flow_style=False)
        
        print(f"\n✅ Business Value Report Exported: {export_path}")
        print(f"\n📊 EXECUTIVE SUMMARY ({days}-day period)")
        print(f"   Engineer: {engineer_profile['name']} ({engineer_profile['email']})")
        print(f"   Machine: {engineer_profile['hostname']} ({engineer_profile['platform']})")
        print(f"\n💰 COST SAVINGS")
        print(f"   Total Saved: ${cost_savings['total_saved_usd']:.2f}")
        print(f"   Annual Projection: ${(cost_savings['total_saved_usd']/days)*365:.2f}")
        print(f"   Tokens Saved: {cost_savings['total_tokens_saved']:,}")
        print(f"\n⏱️  TIME SAVINGS")
        print(f"   Total Time Saved: {cost_savings['total_time_saved_minutes']/60:.1f} hours")
        print(f"   Daily Average: {cost_savings['total_time_saved_minutes']/60/days:.1f} hours/day")
        print(f"\n� PRODUCTIVITY")
        print(f"   Commits: {productivity_metrics['total_commits']} ({productivity_metrics['total_commits']/days:.1f}/day)")
        print(f"   PRs Merged: {productivity_metrics['total_prs_merged']}")
        print(f"   Test Coverage: {productivity_metrics['avg_test_coverage']:.1f}%")
        print(f"\n🚀 COPILOT ENHANCEMENT")
        print(f"   Memory Hit Rate: {copilot_metrics['memory_hit_rate']:.1%}")
        print(f"   Suggestion Acceptance: {copilot_metrics['acceptance_rate']:.1%}")
        print(f"\n🏆 ROI: {roi_analysis['roi_multiplier']:.1f}x return on investment\n")
        
        return export_path
    
    def setup_engineer_profile(
        self,
        engineer_name: str,
        engineer_email: str
    ) -> Dict[str, Any]:
        """
        Setup engineer profile for telemetry (one-time setup).
        
        Args:
            engineer_name: Full name (e.g., "John Smith")
            engineer_email: Work email (e.g., "john.smith@company.com")
        
        Returns:
            Confirmation with profile details
        """
        # Collect machine info
        profile = EngineerProfile(
            engineer_name=engineer_name,
            engineer_email=engineer_email,
            machine_hostname=socket.gethostname(),
            machine_platform=platform.system(),
            cpu_info=self._get_cpu_info(),
            ram_gb=self._get_ram_gb(),
            python_version=f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            cortex_version=self._get_cortex_version(),
            installation_date=datetime.now()
        )
        
        # Save to database
        db_path = self._get_telemetry_db_path()
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO engineer_profile (
                engineer_name,
                engineer_email,
                machine_hostname,
                machine_platform,
                cpu_info,
                ram_gb,
                python_version,
                cortex_version,
                installation_date,
                last_updated
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            profile.engineer_name,
            profile.engineer_email,
            profile.machine_hostname,
            profile.machine_platform,
            profile.cpu_info,
            profile.ram_gb,
            profile.python_version,
            profile.cortex_version,
            profile.installation_date.isoformat(),
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
        
        # Enable telemetry
        config_path = self._get_config_path()
        config = self._load_config(config_path)
        
        if "telemetry" not in config:
            config["telemetry"] = {}
        
        config["telemetry"]["enabled"] = True
        config["telemetry"]["engineer_email"] = engineer_email
        config["telemetry"]["setup_date"] = datetime.now().isoformat()
        
        self._save_config(config, config_path)
        
        logger.info(f"Engineer profile created: {engineer_email}")
        
        return {
            "success": True,
            "message": "Engineer profile created and telemetry enabled",
            "profile": {
                "name": profile.engineer_name,
                "email": profile.engineer_email,
                "machine": profile.machine_hostname,
                "platform": profile.machine_platform,
                "cpu": profile.cpu_info,
                "ram_gb": profile.ram_gb
            },
            "what_is_tracked": [
                "Performance metrics (latency, success rates)",
                "Cost savings (tokens saved, API costs avoided)",
                "Productivity (commits, PRs, velocity)",
                "Copilot enhancement (memory hits, context usage)",
                "Quality improvements (test coverage, bug fixes)"
            ]
        }
    
    def disable_telemetry(self) -> Dict[str, Any]:
        """
        Disable telemetry.
        
        Returns:
            Confirmation message
        """
        config_path = self._get_config_path()
        config = self._load_config(config_path)
        
        if "telemetry" not in config:
            config["telemetry"] = {}
        
        config["telemetry"]["enabled"] = False
        
        self._save_config(config, config_path)
        
        logger.info("Performance telemetry disabled by user")
        
        return {
            "success": True,
            "message": "Performance telemetry disabled",
            "note": "Existing metrics retained (can still export)"
        }
    
    def get_telemetry_status(self) -> Dict[str, Any]:
        """
        Get current telemetry status.
        
        Returns:
            Status information
        """
        config = self._load_config(self._get_config_path())
        enabled = config.get("telemetry", {}).get("enabled", False)
        consent_date = config.get("telemetry", {}).get("consent_date")
        
        # Count metrics
        db_path = self._get_telemetry_db_path()
        metric_count = 0
        capabilities_tracked = set()
        
        if db_path.exists():
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM performance_metrics")
            metric_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT DISTINCT capability FROM performance_metrics")
            capabilities_tracked = {row[0] for row in cursor.fetchall()}
            
            conn.close()
        
        return {
            "enabled": enabled,
            "consent_date": consent_date,
            "metrics_collected": metric_count,
            "capabilities_tracked": len(capabilities_tracked),
            "capabilities_list": sorted(capabilities_tracked),
            "database_path": str(db_path)
        }
    
    # ========================================================================
    # PRIVATE - Database Operations
    # ========================================================================
    
    def _init_database(self, db_path: Path) -> None:
        """Initialize telemetry database schema with comprehensive metrics"""
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Engineer profile table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS engineer_profile (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                engineer_name TEXT NOT NULL,
                engineer_email TEXT UNIQUE NOT NULL,
                machine_hostname TEXT NOT NULL,
                machine_platform TEXT NOT NULL,
                cpu_info TEXT,
                ram_gb INTEGER,
                python_version TEXT,
                cortex_version TEXT,
                installation_date TEXT,
                last_updated TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Performance metrics table (enhanced)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS performance_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                engineer_email TEXT NOT NULL,
                capability TEXT NOT NULL,
                duration_ms REAL NOT NULL,
                success INTEGER NOT NULL,
                error_type TEXT,
                tokens_saved INTEGER DEFAULT 0,
                context_size_tokens INTEGER DEFAULT 0,
                timestamp TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (engineer_email) REFERENCES engineer_profile(engineer_email)
            )
        """)
        
        # Productivity metrics table (NEW)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS productivity_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                engineer_email TEXT NOT NULL,
                metric_date TEXT NOT NULL,
                commits_count INTEGER DEFAULT 0,
                prs_created INTEGER DEFAULT 0,
                prs_merged INTEGER DEFAULT 0,
                lines_added INTEGER DEFAULT 0,
                lines_deleted INTEGER DEFAULT 0,
                test_coverage_percent REAL DEFAULT 0,
                bugs_fixed INTEGER DEFAULT 0,
                code_reviews_completed INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (engineer_email) REFERENCES engineer_profile(engineer_email),
                UNIQUE(engineer_email, metric_date)
            )
        """)
        
        # Cost savings table (NEW)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cost_savings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                engineer_email TEXT NOT NULL,
                metric_date TEXT NOT NULL,
                tokens_saved_count INTEGER DEFAULT 0,
                api_calls_avoided INTEGER DEFAULT 0,
                estimated_cost_saved_usd REAL DEFAULT 0,
                time_saved_minutes INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (engineer_email) REFERENCES engineer_profile(engineer_email),
                UNIQUE(engineer_email, metric_date)
            )
        """)
        
        # Copilot enhancement metrics table (NEW)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS copilot_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                engineer_email TEXT NOT NULL,
                metric_date TEXT NOT NULL,
                memory_hits INTEGER DEFAULT 0,
                memory_misses INTEGER DEFAULT 0,
                context_injections INTEGER DEFAULT 0,
                avg_context_tokens INTEGER DEFAULT 0,
                suggestions_accepted INTEGER DEFAULT 0,
                suggestions_rejected INTEGER DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (engineer_email) REFERENCES engineer_profile(engineer_email),
                UNIQUE(engineer_email, metric_date)
            )
        """)
        
        # Indexes for fast queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_metrics_engineer_capability 
            ON performance_metrics(engineer_email, capability)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_metrics_timestamp 
            ON performance_metrics(timestamp DESC)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_productivity_engineer_date 
            ON productivity_metrics(engineer_email, metric_date DESC)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_cost_engineer_date 
            ON cost_savings(engineer_email, metric_date DESC)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_copilot_engineer_date 
            ON copilot_metrics(engineer_email, metric_date DESC)
        """)
        
        conn.commit()
        conn.close()
    
    def _record_metric(
        self,
        capability: str,
        duration_ms: float,
        success: bool,
        error_type: Optional[str],
        timestamp: datetime,
        tokens_saved: int = 0,
        context_size_tokens: int = 0
    ) -> None:
        """Record single performance metric to database with engineer attribution"""
        db_path = self._get_telemetry_db_path()
        engineer_email = self._get_engineer_email()
        
        if not engineer_email:
            logger.warning("No engineer profile setup - skipping metric recording")
            return
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO performance_metrics (
                engineer_email,
                capability,
                duration_ms,
                success,
                error_type,
                tokens_saved,
                context_size_tokens,
                timestamp
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            engineer_email,
            capability,
            duration_ms,
            1 if success else 0,
            error_type,
            tokens_saved,
            context_size_tokens,
            timestamp.isoformat()
        ))
        
        conn.commit()
        conn.close()
    
    def record_productivity_metrics(
        self,
        commits_count: int = 0,
        prs_created: int = 0,
        prs_merged: int = 0,
        lines_added: int = 0,
        lines_deleted: int = 0,
        test_coverage_percent: float = 0,
        bugs_fixed: int = 0,
        code_reviews_completed: int = 0
    ) -> Dict[str, Any]:
        """
        Record daily productivity metrics.
        
        Call this at end of day or via automated git hook.
        """
        engineer_email = self._get_engineer_email()
        if not engineer_email:
            return {"success": False, "error": "Engineer profile not setup"}
        
        db_path = self._get_telemetry_db_path()
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        today = datetime.now().date().isoformat()
        
        cursor.execute("""
            INSERT OR REPLACE INTO productivity_metrics (
                engineer_email,
                metric_date,
                commits_count,
                prs_created,
                prs_merged,
                lines_added,
                lines_deleted,
                test_coverage_percent,
                bugs_fixed,
                code_reviews_completed
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            engineer_email,
            today,
            commits_count,
            prs_created,
            prs_merged,
            lines_added,
            lines_deleted,
            test_coverage_percent,
            bugs_fixed,
            code_reviews_completed
        ))
        
        conn.commit()
        conn.close()
        
        return {"success": True, "date": today}
    
    def record_cost_savings(
        self,
        tokens_saved_count: int = 0,
        api_calls_avoided: int = 0,
        time_saved_minutes: int = 0
    ) -> Dict[str, Any]:
        """
        Record daily cost savings metrics.
        
        Calculates estimated USD savings based on GPT-4 pricing.
        """
        engineer_email = self._get_engineer_email()
        if not engineer_email:
            return {"success": False, "error": "Engineer profile not setup"}
        
        # Calculate cost saved (GPT-4 pricing: ~$0.03/1K input tokens)
        estimated_cost_saved_usd = (tokens_saved_count / 1000) * 0.03
        
        db_path = self._get_telemetry_db_path()
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        today = datetime.now().date().isoformat()
        
        cursor.execute("""
            INSERT OR REPLACE INTO cost_savings (
                engineer_email,
                metric_date,
                tokens_saved_count,
                api_calls_avoided,
                estimated_cost_saved_usd,
                time_saved_minutes
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (
            engineer_email,
            today,
            tokens_saved_count,
            api_calls_avoided,
            estimated_cost_saved_usd,
            time_saved_minutes
        ))
        
        conn.commit()
        conn.close()
        
        return {
            "success": True,
            "date": today,
            "cost_saved_usd": round(estimated_cost_saved_usd, 2)
        }
    
    def record_copilot_metrics(
        self,
        memory_hits: int = 0,
        memory_misses: int = 0,
        context_injections: int = 0,
        avg_context_tokens: int = 0,
        suggestions_accepted: int = 0,
        suggestions_rejected: int = 0
    ) -> Dict[str, Any]:
        """
        Record Copilot enhancement metrics.
        
        Tracks how CORTEX improves GitHub Copilot performance.
        """
        engineer_email = self._get_engineer_email()
        if not engineer_email:
            return {"success": False, "error": "Engineer profile not setup"}
        
        db_path = self._get_telemetry_db_path()
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        today = datetime.now().date().isoformat()
        
        cursor.execute("""
            INSERT OR REPLACE INTO copilot_metrics (
                engineer_email,
                metric_date,
                memory_hits,
                memory_misses,
                context_injections,
                avg_context_tokens,
                suggestions_accepted,
                suggestions_rejected
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            engineer_email,
            today,
            memory_hits,
            memory_misses,
            context_injections,
            avg_context_tokens,
            suggestions_accepted,
            suggestions_rejected
        ))
        
        conn.commit()
        conn.close()
        
        memory_hit_rate = memory_hits / (memory_hits + memory_misses) if (memory_hits + memory_misses) > 0 else 0
        
        return {
            "success": True,
            "date": today,
            "memory_hit_rate": round(memory_hit_rate, 3)
        }
    
    def _aggregate_metrics(self, since: datetime, engineer_email: str) -> List[Dict[str, Any]]:
        """Aggregate performance metrics by capability for specific engineer"""
        db_path = self._get_telemetry_db_path()
        
        if not db_path.exists():
            return []
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Query metrics for this engineer
        cursor.execute("""
            SELECT 
                capability,
                duration_ms,
                success,
                error_type,
                tokens_saved,
                context_size_tokens,
                timestamp
            FROM performance_metrics
            WHERE engineer_email = ? AND timestamp >= ?
            ORDER BY capability, timestamp
        """, (engineer_email, since.isoformat()))
        
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            return []
        
        # Group by capability
        by_capability = {}
        for row in rows:
            capability = row[0]
            if capability not in by_capability:
                by_capability[capability] = {
                    "durations": [],
                    "successes": 0,
                    "failures": 0,
                    "error_types": {},
                    "total_tokens_saved": 0,
                    "total_context_tokens": 0
                }
            
            by_capability[capability]["durations"].append(row[1])
            if row[2]:  # success
                by_capability[capability]["successes"] += 1
            else:
                by_capability[capability]["failures"] += 1
                error_type = row[3] or "unknown"
                by_capability[capability]["error_types"][error_type] = \
                    by_capability[capability]["error_types"].get(error_type, 0) + 1
            
            by_capability[capability]["total_tokens_saved"] += row[4] or 0
            by_capability[capability]["total_context_tokens"] += row[5] or 0
        
        # Calculate statistics
        result = []
        for capability, data in sorted(by_capability.items()):
            durations = data["durations"]
            total = data["successes"] + data["failures"]
            
            sorted_durations = sorted(durations)
            
            result.append({
                "name": capability,
                "metrics": {
                    "total_executions": total,
                    "success_rate": round(data["successes"] / total, 3) if total > 0 else 0,
                    "avg_execution_time_ms": int(sum(durations) / len(durations)),
                    "p50_latency_ms": int(self._percentile(sorted_durations, 50)),
                    "p95_latency_ms": int(self._percentile(sorted_durations, 95)),
                    "p99_latency_ms": int(self._percentile(sorted_durations, 99)),
                    "min_latency_ms": int(min(durations)),
                    "max_latency_ms": int(max(durations)),
                    "tokens_saved": data["total_tokens_saved"],
                    "avg_context_tokens": int(data["total_context_tokens"] / total) if total > 0 else 0,
                    "error_types": [
                        {"type": err_type, "count": count}
                        for err_type, count in sorted(
                            data["error_types"].items(),
                            key=lambda x: x[1],
                            reverse=True
                        )
                    ],
                    "performance_trend": self._calculate_trend(sorted_durations)
                }
            })
        
        return result
    
    def _get_engineer_profile(self, engineer_email: str) -> Dict[str, Any]:
        """Get engineer profile from database"""
        db_path = self._get_telemetry_db_path()
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                engineer_name,
                engineer_email,
                machine_hostname,
                machine_platform,
                cpu_info,
                ram_gb,
                python_version,
                cortex_version
            FROM engineer_profile
            WHERE engineer_email = ?
        """, (engineer_email,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return {}
        
        return {
            "name": row[0],
            "email": row[1],
            "hostname": row[2],
            "platform": row[3],
            "cpu": row[4],
            "ram_gb": row[5],
            "python_version": row[6],
            "cortex_version": row[7]
        }
    
    def _aggregate_productivity(self, since: datetime, engineer_email: str) -> Dict[str, Any]:
        """Aggregate productivity metrics"""
        db_path = self._get_telemetry_db_path()
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                SUM(commits_count),
                SUM(prs_created),
                SUM(prs_merged),
                SUM(lines_added),
                SUM(lines_deleted),
                AVG(test_coverage_percent),
                SUM(bugs_fixed),
                SUM(code_reviews_completed)
            FROM productivity_metrics
            WHERE engineer_email = ? AND metric_date >= ?
        """, (engineer_email, since.date().isoformat()))
        
        row = cursor.fetchone()
        conn.close()
        
        return {
            "total_commits": row[0] or 0,
            "total_prs": row[1] or 0,
            "total_prs_merged": row[2] or 0,
            "total_lines_added": row[3] or 0,
            "total_lines_deleted": row[4] or 0,
            "avg_test_coverage": round(row[5] or 0, 1),
            "total_bugs_fixed": row[6] or 0,
            "total_code_reviews": row[7] or 0,
            "velocity_trend": "stable"  # TODO: Calculate from historical data
        }
    
    def _aggregate_cost_savings(self, since: datetime, engineer_email: str) -> Dict[str, Any]:
        """Aggregate cost savings"""
        db_path = self._get_telemetry_db_path()
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                SUM(tokens_saved_count),
                SUM(api_calls_avoided),
                SUM(estimated_cost_saved_usd),
                SUM(time_saved_minutes)
            FROM cost_savings
            WHERE engineer_email = ? AND metric_date >= ?
        """, (engineer_email, since.date().isoformat()))
        
        row = cursor.fetchone()
        conn.close()
        
        return {
            "total_tokens_saved": row[0] or 0,
            "total_api_calls_avoided": row[1] or 0,
            "total_saved_usd": row[2] or 0.0,
            "total_time_saved_minutes": row[3] or 0
        }
    
    def _aggregate_copilot_metrics(self, since: datetime, engineer_email: str) -> Dict[str, Any]:
        """Aggregate Copilot enhancement metrics"""
        db_path = self._get_telemetry_db_path()
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                SUM(memory_hits),
                SUM(memory_misses),
                SUM(context_injections),
                AVG(avg_context_tokens),
                SUM(suggestions_accepted),
                SUM(suggestions_rejected)
            FROM copilot_metrics
            WHERE engineer_email = ? AND metric_date >= ?
        """, (engineer_email, since.date().isoformat()))
        
        row = cursor.fetchone()
        conn.close()
        
        memory_hits = row[0] or 0
        memory_misses = row[1] or 0
        suggestions_accepted = row[4] or 0
        suggestions_rejected = row[5] or 0
        
        memory_hit_rate = memory_hits / (memory_hits + memory_misses) if (memory_hits + memory_misses) > 0 else 0
        acceptance_rate = suggestions_accepted / (suggestions_accepted + suggestions_rejected) if (suggestions_accepted + suggestions_rejected) > 0 else 0
        
        return {
            "total_memory_hits": memory_hits,
            "total_memory_misses": memory_misses,
            "memory_hit_rate": memory_hit_rate,
            "total_context_injections": row[2] or 0,
            "avg_context_tokens": int(row[3] or 0),
            "total_suggestions_accepted": suggestions_accepted,
            "total_suggestions_rejected": suggestions_rejected,
            "acceptance_rate": acceptance_rate
        }
    
    def _calculate_roi(
        self,
        cost_savings: Dict[str, Any],
        productivity: Dict[str, Any],
        days: int
    ) -> Dict[str, Any]:
        """
        Calculate return on investment.
        
        Assumes CORTEX cost: $50/month/engineer (conservative estimate)
        """
        cortex_monthly_cost = 50  # USD per engineer
        cortex_cost_period = (days / 30) * cortex_monthly_cost
        
        # Total value delivered
        total_value = cost_savings["total_saved_usd"]
        
        # Add productivity value (assume $100/hour engineer cost)
        productivity_value = (cost_savings["total_time_saved_minutes"] / 60) * 100
        total_value += productivity_value
        
        # Calculate ROI
        roi_multiplier = total_value / cortex_cost_period if cortex_cost_period > 0 else 0
        
        # Productivity gain (commits per day vs baseline)
        baseline_commits_per_day = 2.0  # Industry average
        actual_commits_per_day = productivity["total_commits"] / days if days > 0 else 0
        productivity_gain_percent = ((actual_commits_per_day - baseline_commits_per_day) / baseline_commits_per_day) * 100 if baseline_commits_per_day > 0 else 0
        
        # Quality score (0-100)
        quality_score = min(100, (
            (productivity["avg_test_coverage"] * 0.4) +  # 40% weight on test coverage
            (min(productivity["total_bugs_fixed"], 20) * 2.0) +  # 40% weight on bug fixes (cap at 20)
            (min(productivity["total_code_reviews"], 10) * 2.0)  # 20% weight on code reviews (cap at 10)
        ))
        
        return {
            "cortex_cost_period_usd": round(cortex_cost_period, 2),
            "total_value_delivered_usd": round(total_value, 2),
            "roi_multiplier": round(roi_multiplier, 1),
            "productivity_gain_percent": round(productivity_gain_percent, 1),
            "commits_per_day": round(actual_commits_per_day, 2),
            "quality_score": round(quality_score, 1),
            "recommendation": (
                "Strong ROI - Continue CORTEX investment" if roi_multiplier >= 2.0
                else "Positive ROI - CORTEX delivering value" if roi_multiplier >= 1.0
                else "Monitor usage - Consider increasing CORTEX utilization"
            )
        }
    
    def _percentile(self, sorted_values: List[float], percentile: int) -> float:
        """Calculate percentile from sorted values"""
        if not sorted_values:
            return 0
        
        index = (percentile / 100) * (len(sorted_values) - 1)
        lower = int(index)
        upper = lower + 1
        
        if upper >= len(sorted_values):
            return sorted_values[-1]
        
        weight = index - lower
        return sorted_values[lower] * (1 - weight) + sorted_values[upper] * weight
    
    def _calculate_trend(self, durations: List[float]) -> str:
        """
        Calculate performance trend.
        
        Returns: "improving", "stable", or "degrading"
        """
        if len(durations) < 10:
            return "insufficient_data"
        
        # Compare first half vs second half
        midpoint = len(durations) // 2
        first_half_avg = sum(durations[:midpoint]) / midpoint
        second_half_avg = sum(durations[midpoint:]) / (len(durations) - midpoint)
        
        change_pct = (second_half_avg - first_half_avg) / first_half_avg
        
        if change_pct < -0.15:  # >15% faster
            return "improving"
        elif change_pct > 0.15:  # >15% slower
            return "degrading"
        else:
            return "stable"
    
    # ========================================================================
    # PRIVATE - Context & Configuration
    # ========================================================================
    
    def _has_user_consent(self) -> bool:
        """Check if telemetry is enabled"""
        config = self._load_config(self._get_config_path())
        return config.get("telemetry", {}).get("enabled", False)
    
    def _get_engineer_email(self) -> Optional[str]:
        """Get engineer email from config"""
        config = self._load_config(self._get_config_path())
        return config.get("telemetry", {}).get("engineer_email")
    
    def _get_cpu_info(self) -> str:
        """Get CPU information"""
        try:
            if platform.system() == "Windows":
                return platform.processor()
            elif platform.system() == "Darwin":  # macOS
                cmd = "sysctl -n machdep.cpu.brand_string"
                return subprocess.check_output(cmd, shell=True).decode().strip()
            else:  # Linux
                cmd = "cat /proc/cpuinfo | grep 'model name' | uniq"
                result = subprocess.check_output(cmd, shell=True).decode().strip()
                return result.split(":")[1].strip() if ":" in result else "Unknown"
        except Exception:
            return f"{platform.processor()} (details unavailable)"
    
    def _get_ram_gb(self) -> int:
        """Get RAM in GB"""
        try:
            if platform.system() == "Windows":
                import ctypes
                kernel32 = ctypes.windll.kernel32
                c_ulong = ctypes.c_ulong
                class MEMORYSTATUSEX(ctypes.Structure):
                    _fields_ = [
                        ('dwLength', c_ulong),
                        ('dwMemoryLoad', c_ulong),
                        ('ullTotalPhys', ctypes.c_ulonglong),
                        ('ullAvailPhys', ctypes.c_ulonglong),
                        ('ullTotalPageFile', ctypes.c_ulonglong),
                        ('ullAvailPageFile', ctypes.c_ulonglong),
                        ('ullTotalVirtual', ctypes.c_ulonglong),
                        ('ullAvailVirtual', ctypes.c_ulonglong),
                        ('sullAvailExtendedVirtual', ctypes.c_ulonglong),
                    ]
                memoryStatus = MEMORYSTATUSEX()
                memoryStatus.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
                kernel32.GlobalMemoryStatusEx(ctypes.byref(memoryStatus))
                return int(memoryStatus.ullTotalPhys / (1024**3))
            elif platform.system() == "Darwin":  # macOS
                cmd = "sysctl -n hw.memsize"
                bytes_ram = int(subprocess.check_output(cmd, shell=True).decode().strip())
                return int(bytes_ram / (1024**3))
            else:  # Linux
                with open('/proc/meminfo', 'r') as f:
                    for line in f:
                        if line.startswith('MemTotal'):
                            kb = int(line.split()[1])
                            return int(kb / (1024**2))
        except Exception:
            return 0  # Unknown
        return 0
    
    def _get_cortex_version(self) -> str:
        """Get CORTEX version"""
        # Try to read from version file or package
        version_file = Path(__file__).parent.parent.parent / "VERSION"
        if version_file.exists():
            return version_file.read_text().strip()
        return "2.0.5"  # Default
    
    def _get_platform(self) -> str:
        """Get platform identifier"""
        return platform.system()  # "Windows", "Darwin", "Linux"
    

    
    # ========================================================================
    # PRIVATE - Utilities
    # ========================================================================
    
    def _get_telemetry_db_path(self) -> Path:
        """Get path to telemetry database"""
        # Store in cortex-brain/tier3 (context data)
        cortex_root = self._get_cortex_root()
        return cortex_root / "cortex-brain" / "tier3" / "performance_telemetry.db"
    
    def _get_config_path(self) -> Path:
        """Get path to cortex config"""
        return self._get_cortex_root() / "cortex.config.json"
    
    def _get_cortex_root(self) -> Path:
        """Get CORTEX repository root"""
        # Navigate up from plugin file
        return Path(__file__).parent.parent.parent
    
    def _get_project_root(self) -> Path:
        """Get current project root (where CORTEX is working)"""
        # For now, same as CORTEX root (self-documenting)
        # In production, this would be the user's project
        return self._get_cortex_root()
    
    def _load_config(self, path: Path) -> Dict[str, Any]:
        """Load configuration file"""
        if not path.exists():
            return {}
        
        import json
        with open(path, 'r') as f:
            return json.load(f)
    
    def _save_config(self, config: Dict[str, Any], path: Path) -> None:
        """Save configuration file"""
        import json
        with open(path, 'w') as f:
            json.dump(config, f, indent=2)


# Plugin registration
def register() -> BasePlugin:
    """Register plugin with CORTEX"""
    return PerformanceTelemetryPlugin()
