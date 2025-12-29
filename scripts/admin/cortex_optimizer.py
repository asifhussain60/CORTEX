#!/usr/bin/env python3
"""
CORTEX Admin Optimizer
======================

Admin-only tool for analyzing and optimizing the CORTEX codebase.
NOT packaged for deployment - development use only.

Features:
- Token usage analysis (prompts, YAML files)
- YAML validation (brain files, knowledge graph)
- Plugin health checks (metadata, registration)
- Conversation DB optimization (indexes, cleanup)
- Code metrics aggregation (wraps radon/pylint/vulture)

Usage:
    python scripts/admin/cortex_optimizer.py analyze [--report json]
    python scripts/admin/cortex_optimizer.py refactor --dry-run
    python scripts/admin/cortex_optimizer.py profile --module tier1
    python scripts/admin/cortex_optimizer.py cleanup --interactive

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
import yaml
import sqlite3
from dataclasses import dataclass, asdict
import re
from collections import defaultdict

# Add CORTEX root to path
CORTEX_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(CORTEX_ROOT))


@dataclass
class OptimizationResult:
    """Results from optimization analysis."""
    category: str
    score: int  # 0-100
    issues: List[str]
    recommendations: List[str]
    metrics: Dict[str, Any]


class TokenAnalyzer:
    """Analyzes token usage in prompts and YAML files."""
    
    PROMPT_DIR = CORTEX_ROOT / "prompts"
    BRAIN_DIR = CORTEX_ROOT / "cortex-brain"
    
    # Rough token estimation (GPT-4 tokenization ~1.3 chars/token)
    CHARS_PER_TOKEN = 1.3
    
    def analyze(self) -> OptimizationResult:
        """Analyze token usage across CORTEX documentation."""
        issues = []
        recommendations = []
        metrics = {}
        
        # Analyze prompt files
        prompt_files = list(self.PROMPT_DIR.rglob("*.md"))
        total_tokens = 0
        large_files = []
        
        for pfile in prompt_files:
            content = pfile.read_text(encoding="utf-8")
            tokens = len(content) / self.CHARS_PER_TOKEN
            total_tokens += tokens
            
            if tokens > 5000:
                large_files.append((pfile.name, int(tokens)))
                issues.append(f"Large prompt file: {pfile.name} ({int(tokens)} tokens)")
        
        # Analyze YAML brain files
        yaml_files = list(self.BRAIN_DIR.glob("*.yaml"))
        yaml_tokens = 0
        
        for yfile in yaml_files:
            content = yfile.read_text(encoding="utf-8")
            yaml_tokens += len(content) / self.CHARS_PER_TOKEN
        
        # Calculate score (lower tokens = better)
        avg_prompt_size = total_tokens / len(prompt_files) if prompt_files else 0
        score = max(0, 100 - int(avg_prompt_size / 50))  # Penalize files >5000 tokens
        
        # Recommendations
        if large_files:
            recommendations.append("Split large prompt files into modular components")
        if yaml_tokens > 10000:
            recommendations.append("Consider compressing YAML brain files")
        
        metrics = {
            "total_prompt_tokens": int(total_tokens),
            "total_yaml_tokens": int(yaml_tokens),
            "avg_prompt_size": int(avg_prompt_size),
            "prompt_file_count": len(prompt_files),
            "large_files": large_files
        }
        
        return OptimizationResult(
            category="Token Usage",
            score=score,
            issues=issues,
            recommendations=recommendations,
            metrics=metrics
        )


class YAMLValidator:
    """Validates CORTEX YAML brain files."""
    
    BRAIN_DIR = CORTEX_ROOT / "cortex-brain"
    
    REQUIRED_FIELDS = {
        "knowledge-graph.yaml": ["patterns", "version"],
        "brain-protection-rules.yaml": ["rules", "version"],
        "capabilities.yaml": ["version"],
    }
    
    def analyze(self) -> OptimizationResult:
        """Validate YAML structure and schema compliance."""
        issues = []
        recommendations = []
        metrics = {}
        
        yaml_files = list(self.BRAIN_DIR.glob("*.yaml"))
        valid_count = 0
        invalid_files = []
        
        for yfile in yaml_files:
            try:
                with open(yfile, 'r', encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                
                # Check if empty or malformed
                if not data:
                    issues.append(f"Empty YAML file: {yfile.name}")
                    invalid_files.append(yfile.name)
                    continue
                
                # Check required fields for known schemas
                if yfile.name in self.REQUIRED_FIELDS:
                    required = self.REQUIRED_FIELDS[yfile.name]
                    missing = [f for f in required if f not in data]
                    if missing:
                        issues.append(f"{yfile.name} missing fields: {', '.join(missing)}")
                        invalid_files.append(yfile.name)
                        continue
                
                valid_count += 1
                
            except yaml.YAMLError as e:
                issues.append(f"YAML parse error in {yfile.name}: {e}")
                invalid_files.append(yfile.name)
        
        # Calculate score
        score = int((valid_count / len(yaml_files)) * 100) if yaml_files else 100
        
        # Recommendations
        if invalid_files:
            recommendations.append("Fix YAML validation errors before deployment")
        if score < 80:
            recommendations.append("Add schema validation tests for brain files")
        
        metrics = {
            "total_yaml_files": len(yaml_files),
            "valid_files": valid_count,
            "invalid_files": invalid_files,
            "validation_rate": f"{score}%"
        }
        
        return OptimizationResult(
            category="YAML Validation",
            score=score,
            issues=issues,
            recommendations=recommendations,
            metrics=metrics
        )


class PluginHealthChecker:
    """Checks health of CORTEX plugin system."""
    
    PLUGIN_DIR = CORTEX_ROOT / "src" / "plugins"
    
    def analyze(self) -> OptimizationResult:
        """Analyze plugin health and completeness."""
        issues = []
        recommendations = []
        metrics = {}
        
        # Find all plugin files
        plugin_files = [f for f in self.PLUGIN_DIR.glob("*_plugin.py") 
                       if f.name != "base_plugin.py"]
        
        registered_count = 0
        missing_metadata = []
        missing_register = []
        
        for pfile in plugin_files:
            content = pfile.read_text(encoding="utf-8")
            
            # Check for register() function
            if "def register()" not in content:
                issues.append(f"Missing register() in {pfile.name}")
                missing_register.append(pfile.name)
                continue
            
            # Check for PluginMetadata
            if "PluginMetadata" not in content:
                issues.append(f"Missing PluginMetadata in {pfile.name}")
                missing_metadata.append(pfile.name)
                continue
            
            # Check for BasePlugin inheritance
            if "BasePlugin" not in content:
                issues.append(f"Not inheriting from BasePlugin: {pfile.name}")
                continue
            
            registered_count += 1
        
        # Calculate score
        score = int((registered_count / len(plugin_files)) * 100) if plugin_files else 100
        
        # Recommendations
        if missing_register:
            recommendations.append("Add register() function to incomplete plugins")
        if missing_metadata:
            recommendations.append("Add PluginMetadata to plugins for discoverability")
        if score < 90:
            recommendations.append("Review plugin architecture compliance")
        
        metrics = {
            "total_plugins": len(plugin_files),
            "registered_plugins": registered_count,
            "missing_metadata": missing_metadata,
            "missing_register": missing_register,
            "health_score": f"{score}%"
        }
        
        return OptimizationResult(
            category="Plugin Health",
            score=score,
            issues=issues,
            recommendations=recommendations,
            metrics=metrics
        )


class ConversationDBOptimizer:
    """Optimizes CORTEX conversation SQLite database."""
    
    DB_PATH = CORTEX_ROOT / "cortex-brain" / "conversation-history.db"
    
    def analyze(self) -> OptimizationResult:
        """Analyze database health and optimization opportunities."""
        issues = []
        recommendations = []
        metrics = {}
        
        if not self.DB_PATH.exists():
            return OptimizationResult(
                category="Database Optimization",
                score=100,
                issues=["Database not initialized yet"],
                recommendations=["No action needed until DB exists"],
                metrics={"status": "not_initialized"}
            )
        
        try:
            conn = sqlite3.connect(self.DB_PATH)
            cursor = conn.cursor()
            
            # Check table count
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            
            # Check indexes
            cursor.execute("SELECT name FROM sqlite_master WHERE type='index'")
            indexes = cursor.fetchall()
            
            # Check row counts
            row_counts = {}
            for table in tables:
                table_name = table[0]
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                row_counts[table_name] = cursor.fetchone()[0]
            
            # Check database size
            cursor.execute("PRAGMA page_count")
            page_count = cursor.fetchone()[0]
            cursor.execute("PRAGMA page_size")
            page_size = cursor.fetchone()[0]
            db_size_mb = (page_count * page_size) / (1024 * 1024)
            
            # Analyze vacuum need
            cursor.execute("PRAGMA freelist_count")
            freelist_count = cursor.fetchone()[0]
            fragmentation_pct = (freelist_count / page_count * 100) if page_count else 0
            
            conn.close()
            
            # Score calculation
            score = 100
            
            # Penalize missing indexes
            expected_indexes = 2  # Assume we need at least 2 indexes
            if len(indexes) < expected_indexes:
                issues.append(f"Only {len(indexes)} indexes found (expected {expected_indexes})")
                score -= 20
                recommendations.append("Add indexes on timestamp and event_type columns")
            
            # Penalize fragmentation
            if fragmentation_pct > 10:
                issues.append(f"Database fragmentation: {fragmentation_pct:.1f}%")
                score -= 15
                recommendations.append("Run VACUUM to defragment database")
            
            # Penalize large size
            if db_size_mb > 100:
                issues.append(f"Large database size: {db_size_mb:.1f} MB")
                score -= 10
                recommendations.append("Consider archiving old conversations")
            
            metrics = {
                "table_count": len(tables),
                "index_count": len(indexes),
                "row_counts": row_counts,
                "size_mb": round(db_size_mb, 2),
                "fragmentation_pct": round(fragmentation_pct, 1)
            }
            
        except sqlite3.Error as e:
            issues.append(f"Database error: {e}")
            score = 50
            recommendations.append("Check database integrity")
            metrics = {"error": str(e)}
        
        return OptimizationResult(
            category="Database Optimization",
            score=max(0, score),
            issues=issues,
            recommendations=recommendations,
            metrics=metrics
        )


class CortexOptimizer:
    """Main optimizer orchestrator."""
    
    def __init__(self):
        self.analyzers = [
            TokenAnalyzer(),
            YAMLValidator(),
            PluginHealthChecker(),
            ConversationDBOptimizer()
        ]
    
    def analyze(self, report_format: str = "text") -> Dict[str, Any]:
        """Run all analyzers and generate report."""
        results = []
        
        print("🔍 CORTEX Codebase Optimization Analysis")
        print("=" * 60)
        print()
        
        for analyzer in self.analyzers:
            result = analyzer.analyze()
            results.append(result)
            
            if report_format == "text":
                self._print_result(result)
        
        # Overall score
        overall_score = sum(r.score for r in results) / len(results)
        
        if report_format == "json":
            return {
                "overall_score": int(overall_score),
                "results": [asdict(r) for r in results]
            }
        else:
            print()
            print("=" * 60)
            print(f"🎯 Overall Optimization Score: {int(overall_score)}/100")
            print()
            
            # Aggregated recommendations
            all_recommendations = []
            for r in results:
                all_recommendations.extend(r.recommendations)
            
            if all_recommendations:
                print("📋 Priority Recommendations:")
                for i, rec in enumerate(all_recommendations[:5], 1):
                    print(f"   {i}. {rec}")
            
            return {"overall_score": int(overall_score)}
    
    def _print_result(self, result: OptimizationResult):
        """Print single analysis result."""
        status_emoji = "✅" if result.score >= 80 else "⚠️" if result.score >= 60 else "❌"
        print(f"{status_emoji} {result.category}: {result.score}/100")
        
        if result.issues:
            print(f"   Issues ({len(result.issues)}):")
            for issue in result.issues[:3]:  # Show top 3
                print(f"      • {issue}")
            if len(result.issues) > 3:
                print(f"      ... and {len(result.issues) - 3} more")
        
        if result.recommendations:
            print(f"   Recommendations:")
            for rec in result.recommendations[:2]:  # Show top 2
                print(f"      → {rec}")
        
        print()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="CORTEX Admin Optimizer - Analyze and optimize codebase",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Run optimization analysis")
    analyze_parser.add_argument(
        "--report",
        choices=["text", "json"],
        default="text",
        help="Report format (default: text)"
    )
    
    # Refactor command (placeholder)
    refactor_parser = subparsers.add_parser("refactor", help="Automated refactoring")
    refactor_parser.add_argument("--dry-run", action="store_true", help="Show changes without applying")
    
    # Profile command (placeholder)
    profile_parser = subparsers.add_parser("profile", help="Performance profiling")
    profile_parser.add_argument("--module", help="Module to profile")
    
    # Cleanup command (placeholder)
    cleanup_parser = subparsers.add_parser("cleanup", help="Cleanup unused code")
    cleanup_parser.add_argument("--interactive", action="store_true", help="Interactive mode")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    optimizer = CortexOptimizer()
    
    if args.command == "analyze":
        result = optimizer.analyze(report_format=args.report)
        if args.report == "json":
            print(json.dumps(result, indent=2))
    
    elif args.command == "refactor":
        print("🚧 Refactor command coming soon!")
        print("   This will suggest automated code improvements.")
    
    elif args.command == "profile":
        print("🚧 Profile command coming soon!")
        print("   This will analyze performance bottlenecks.")
    
    elif args.command == "cleanup":
        print("🚧 Cleanup command coming soon!")
        print("   This will identify and remove dead code.")


if __name__ == "__main__":
    main()
